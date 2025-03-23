"""
Service for calculating IB commissions based on rules and deal tickets.
"""
from shared_models.ib_commission.models import IBCommissionRule, CommissionDistribution, IBAgreement, IBAgreementMember
from shared_models.ib_commission.models import IBHierarchy, ClientIBMapping, IBAccountAgreement, CommissionTracking
from shared_models.accounts.models import Account
from shared_models.transactions.models import CommissionRebateTransaction
from decimal import Decimal
from datetime import datetime
from django.db import transaction
from django.db.models import Q
from django.db import models
import logging

logger = logging.getLogger(__name__)


class CommissionCalculatorService:
    """
    Service for calculating IB commissions based on rules and deal tickets.
    """
    
    COMMISSION_TYPE = "COMMISSION"
    REBATE_TYPE = "REBATE"
    
    # MT5 entry types
    ENTRY_IN = 0      # Entering the market or adding volume
    ENTRY_OUT = 1     # Exit from the market or partial closure
    ENTRY_INOUT = 2   # Deal that closed an existing position and opened a new one in the opposite direction
    ENTRY_OUT_BY = 3  # Close by - simultaneous closure of two opposite positions
    
    @classmethod
    def calculate_distribution(cls, deal_data):
        """
        Calculate commission distribution for a deal.
        
        Args:
            deal_data: Dictionary containing MT5 deal data
                - deal: MT5 deal ID
                - login: MT5 account login
                - action: 0 (buy) or 1 (sell)
                - entry: Entry type (0=in, 1=out, 2=inout, 3=out_by)
                - symbol: Trading symbol
                - volume: Trading volume
                - price: Deal price
                
        Returns:
            Dictionary containing:
            - distributions: List of calculated distributions
            - client_deduction: Total amount to deduct from client (for entry positions)
            - client_server_id: Server ID for the client account (for MT5 processing)
            - is_processed: Whether distributions have been processed
        """
        # Extract deal data
        deal_ticket = deal_data.get('deal')
        mt5_login = deal_data.get('login')
        action = deal_data.get('action')  # 0=buy, 1=sell
        entry = deal_data.get('entry')    # 0=in, 1=out, 2=inout, 3=out_by
        symbol = deal_data.get('symbol')
        volume = deal_data.get('volume')
        price = deal_data.get('price', 0)
        profit = deal_data.get('profit', 0)
        volume_closed = deal_data.get('volume_closed', volume)
        position_id = deal_data.get('position_id', 0)
        
        # Properly handle timestamp values that come as integers
        trade_time = deal_data.get('time')
        if trade_time is not None:
            # If it's an integer, convert to datetime
            if isinstance(trade_time, int):
                trade_open_time = datetime.fromtimestamp(trade_time)
                trade_close_time = datetime.fromtimestamp(trade_time)
            # If it's already a datetime object, use it directly
            elif isinstance(trade_time, datetime):
                trade_open_time = trade_time
                trade_close_time = trade_time
            # Otherwise, just use the value as is
            else:
                trade_open_time = trade_time
                trade_close_time = trade_time
        else:
            # No time provided
            trade_open_time = None
            trade_close_time = None
        
        # check if action is 0 or 1, convert to int if not
        action = int(action)
        if action != 0 and action != 1:
            print(f"Invalid action: {action}, only 0 or 1 is allowed to be used for rebate/commission calculation")
            return {'distributions': [], 'client_deduction': 0, 'client_server_id': None, 'is_processed': True}
        
        # Convert action to order_type
        order_type = 'buy' if action == 0 else 'sell'
        
        # Check if commission already calculated
        if CommissionDistribution.objects.filter(deal_ticket=deal_ticket).exists():
            return {'distributions': [], 'client_deduction': 0, 'client_server_id': None, 'is_processed': True}
        
        # Try to get account from cache first
        try:
            from shared_models.ib_commission.services.commission_cache_service import CommissionCacheService
            account = CommissionCacheService.get_account(mt5_login)
            logger.info(f"Got account for login {mt5_login} from cache/DB: {account is not None}")
        except (ImportError, Exception) as e:
            logger.warning(f"Could not use CommissionCacheService for account lookup: {e}")
            # Fall back to direct database query
            account = Account.objects.filter(login=mt5_login, is_active=True).first()
            logger.info(f"Got account for login {mt5_login} from direct DB query: {account is not None}")
        
        if not account:
            return {'distributions': [], 'client_deduction': 0, 'client_server_id': None, 'is_processed': False}
        
        # Get customer from account
        customer = account.customer
        
        # Determine which rules to apply based on entry type
        is_entry = entry in [cls.ENTRY_IN, cls.ENTRY_INOUT]  # Entry or InOut
        is_exit = entry in [cls.ENTRY_OUT, cls.ENTRY_OUT_BY]  # Exit or OutBy
        
        # For entry positions, only apply commission rules
        # For exit positions, only apply rebate rules
        rule_filter = {}
        if is_entry:
            rule_filter = {'commission_type': cls.COMMISSION_TYPE}
        elif is_exit:
            rule_filter = {'commission_type': cls.REBATE_TYPE}
        
        # Find applicable rules - this will also find the client mapping
        applicable_rules = cls._find_applicable_rules(
            ib_id=None,  # Will be determined in _find_applicable_rules
            mt5_account_id=mt5_login,
            symbol=symbol, 
            order_type=order_type,  # This is not used for filtering but kept for API compatibility
            customer=customer,
            account=account,
            **rule_filter
        )
        
        if not applicable_rules or not applicable_rules.get('rules'):
            return {'distributions': [], 'client_deduction': 0, 'client_server_id': None, 'is_processed': False}
        
        # Get the client mapping and rules from the result
        client_mapping = applicable_rules.get('client_mapping')
        rules = applicable_rules.get('rules')
        
        if not client_mapping:
            return {'distributions': [], 'client_deduction': 0, 'client_server_id': None, 'is_processed': False}
        
        distributions = []
        client_deduction = Decimal('0.0')
        
        with transaction.atomic():
            # Create commission tracking record with trading details
            commission_tracking = CommissionTracking.objects.create(
                deal_ticket=deal_ticket,
                customer=customer,
                direct_ib_customer=client_mapping.direct_ib_customer,
                client_account=account,
                mt5_login=mt5_login,
                commission_type=cls.COMMISSION_TYPE if is_entry else cls.REBATE_TYPE,
                rule=rules[0],  # Use first rule for tracking
                amount=Decimal('0.0'),  # Will be updated after calculation
                processed_time=datetime.now(),
                # Trading details
                symbol=symbol,
                volume=Decimal(str(volume)) if volume is not None else None,
                volume_closed=Decimal(str(volume_closed)) if volume_closed is not None else None,
                profit=Decimal(str(profit)) if profit is not None else None,
                action=action,
                entry=entry,
                entry_price=Decimal(str(price)) if price is not None else None,
                exit_price=None,  # Will be updated for exit positions if available
                # Set trade open time for entry positions and trade close time for exit positions
                trade_open_time=trade_open_time if is_entry else None,
                trade_close_time=trade_close_time if is_exit else None,
                position_id=position_id
            )
            
            # Get all IBs in the hierarchy path
            ib_hierarchy = IBHierarchy.objects.filter(
                customer=client_mapping.direct_ib_customer,
                is_active=True
            ).first()
            
            if not ib_hierarchy:
                return {'distributions': [], 'client_deduction': 0, 'client_server_id': None, 'is_processed': False}

            path_parts = ib_hierarchy.path.split('.')
            
            # Get all IB agreements in the hierarchy
            ib_agreements = {}
            for ib_id in path_parts:
                agreement_member = IBAgreementMember.objects.filter(
                    customer_id=ib_id,
                    is_active=True
                ).select_related('agreement').first()
                
                if agreement_member:
                    ib_agreements[ib_id] = agreement_member.agreement
            
            # Calculate rule-based distribution
            distributions = cls._calculate_rule_based_distribution(
                deal_ticket=commission_tracking,
                client_mapping=client_mapping,
                ib_agreements=ib_agreements,
                volume=volume,
                commission_usd=Decimal('0.0'),  # Will be calculated based on rules
                customer=customer,
                account=account,
                symbol=symbol,
                is_entry=is_entry,
                is_exit=is_exit
            )
            
            # Calculate total distribution amount for both commission and rebate
            distribution_total = Decimal('0.0')
            if distributions:
                distribution_total = sum(dist.amount for dist in distributions)
            
            # Update commission tracking with total amount - for both commission and rebate
            commission_tracking.amount = distribution_total
            commission_tracking.save()
            
            # Calculate client deduction for entry positions
            if is_entry and distributions:
                client_deduction = cls._calculate_client_deduction(distributions)
        
        # Get client server ID for MT5 processing
        client_server_id = account.server.id if account else None
        
        # Enrich distributions with server information
        for dist in distributions:
            if dist.ib_account and not hasattr(dist, 'server_id'):
                dist.server_id = dist.ib_account.server.id
        
        return {
            'distributions': distributions,
            'client_deduction': client_deduction,
            'client_server_id': client_server_id,
            'is_processed': False
        }

    @classmethod
    def process_distributions(cls, deal_ticket, mt5_processing_success=True, processing_notes=None):
        """
        Process distributions after MT5 side has been processed.
        
        Args:
            deal_ticket: The deal ticket ID
            mt5_processing_success: Whether MT5 processing was successful
            processing_notes: Optional notes about the processing status
            
        Returns:
            Dictionary containing:
            - success: Whether processing was successful
            - transactions: List of created transactions
            - message: Status message
        """
        if not mt5_processing_success:
            # If MT5 processing failed, mark distributions with failed status
            # but don't mark them as processed since they weren't actually credited/debited
            CommissionDistribution.objects.filter(deal_ticket=deal_ticket).update(
                processing_status='FAILED',
                processing_notes=processing_notes or 'MT5 processing failed'
            )
            return {
                'success': False,
                'transactions': [],
                'message': 'MT5 processing failed, distributions marked as failed but not processed'
            }
        
        # Get distributions for this deal ticket that are still pending
        distributions = CommissionDistribution.objects.filter(
            deal_ticket=deal_ticket,
            processing_status='PENDING'
        ).select_related('deal_ticket__customer')
        
        if not distributions:
            return {
                'success': False,
                'transactions': [],
                'message': 'No pending distributions found for this deal ticket'
            }
        
        # Get deal data from the first distribution's deal ticket
        deal_data = {
            'deal': deal_ticket,
            # Add other deal data if available
        }
        
        # Get customer from the first distribution's deal ticket
        customer = distributions.first().deal_ticket.customer
        
        # Create transactions
        transactions = cls._create_transactions(distributions, deal_data, customer)
        
        return {
            'success': True,
            'transactions': transactions,
            'message': f'Successfully processed {len(transactions)} transactions'
        }

    @classmethod
    def _calculate_rule_based_distribution(cls, deal_ticket, client_mapping, 
                                         ib_agreements, volume, commission_usd,
                                         customer, account, symbol,
                                         is_entry=True, is_exit=False):
        """
        Calculate distribution based on individual rules.
        
        Args:
            deal_ticket: The CommissionTracking object
            client_mapping: The ClientIBMapping object
            ib_agreements: Dictionary of IB agreements keyed by IB ID
            volume: The trading volume
            commission_usd: The commission in USD
            is_entry: Boolean indicating if this is an entry position
            is_exit: Boolean indicating if this is an exit position
            
        Returns:
            List of created CommissionDistribution objects
        """
        distributions = []
        
        # Get hierarchy information for all IBs
        hierarchy_info = {}
        for ib_id in ib_agreements.keys():
            hierarchy = IBHierarchy.objects.get(customer_id=ib_id)
            hierarchy_info[ib_id] = {
                'level': hierarchy.level,
                'parent_id': hierarchy.parent_customer_id
            }

        # Process each IB in the hierarchy
        for ib_id, agreement in ib_agreements.items():
            # For entry positions, only apply commission rules
            # For exit positions, only apply rebate rules
            rule_filter = {}
            if is_entry:
                rule_filter = {'commission_type': cls.COMMISSION_TYPE}
            elif is_exit:
                rule_filter = {'commission_type': cls.REBATE_TYPE}
            
            # Find applicable rules for this specific IB
            result = cls._find_applicable_rules(
                ib_id=ib_id,  # Pass the specific IB ID
                mt5_account_id=None,  # Don't use client's account
                symbol=symbol,
                order_type=None,
                customer=None,  # Don't use client's customer
                account=None,   # Don't use client's account
                **rule_filter
            )
            
            applicable_rules = result.get('rules', [])
            
            if not applicable_rules:
                logger.info(f"No applicable rules found for IB {ib_id}")
                continue
            
            # Process each applicable rule
            for rule in applicable_rules:
                # Calculate base amount from rule
                base_amount = cls._calculate_amount_from_rule(
                    rule=rule,
                    volume=volume,
                    commission_usd=commission_usd
                )
                
                if base_amount <= 0:
                    continue

                # Calculate keep amount
                keep_amount = (base_amount * rule.keep_percentage / Decimal('100.0'))
                if keep_amount > 0:
                    # Get IB account
                    ib_hierarchy_entry = IBHierarchy.objects.filter(
                        customer_id=ib_id,
                        is_active=True
                    ).first()
                    
                    ib_account = None
                    mt5_login = 0
                    server_id = None
                    
                    if ib_hierarchy_entry:
                        ib_account = ib_hierarchy_entry.ib_account
                        mt5_login = ib_hierarchy_entry.mt5_login
                        if ib_account:
                            server_id = ib_account.server.id
                    
                    # Create distribution record with server information
                    keep_distribution = CommissionDistribution.objects.create(
                        deal_ticket=deal_ticket,
                        customer_id=ib_id,
                        ib_account=ib_account,
                        mt5_login=mt5_login,
                        distribution_type=rule.commission_type,
                        amount=keep_amount,
                        level=hierarchy_info[ib_id]['level'],
                        rule=rule,
                        is_processed=False,
                        processed_time=datetime.now(),
                        processing_status='PENDING',
                        processing_notes=f'Server ID: {server_id}' if server_id else 'No server information available'
                    )
                    
                    # Add server_id as an attribute for easy access
                    if server_id:
                        keep_distribution.server_id = server_id
                        
                    distributions.append(keep_distribution)

                # Calculate pass-up amount if not master IB
                parent_id = hierarchy_info[ib_id]['parent_id']
                if parent_id and rule.pass_up_percentage > 0:
                    pass_up_amount = (base_amount * rule.pass_up_percentage / Decimal('100.0'))
                    if pass_up_amount > 0:
                        # Get parent IB account
                        parent_hierarchy_entry = IBHierarchy.objects.filter(
                            customer_id=parent_id,
                            is_active=True
                        ).first()
                        
                        parent_account = None
                        parent_mt5_login = 0
                        parent_server_id = None
                        
                        if parent_hierarchy_entry:
                            parent_account = parent_hierarchy_entry.ib_account
                            parent_mt5_login = parent_hierarchy_entry.mt5_login
                            if parent_account:
                                parent_server_id = parent_account.server.id
                        
                        # Create pass-up distribution record with server information
                        pass_up_distribution = CommissionDistribution.objects.create(
                            deal_ticket=deal_ticket,
                            customer_id=parent_id,
                            ib_account=parent_account,
                            mt5_login=parent_mt5_login,
                            distribution_type=rule.commission_type,
                            amount=pass_up_amount,
                            level=hierarchy_info[parent_id]['level'],
                            rule=rule,
                            is_pass_up=True,
                            is_processed=False,
                            processed_time=datetime.now(),
                            processing_status='PENDING',
                            processing_notes=f'Server ID: {parent_server_id}' if parent_server_id else 'No server information available'
                        )
                        
                        # Add server_id as an attribute for easy access
                        if parent_server_id:
                            pass_up_distribution.server_id = parent_server_id
                            
                        distributions.append(pass_up_distribution)
                    
        return distributions

    @classmethod
    def _calculate_amount_from_rule(cls, rule, volume, commission_usd):
        """
        Calculate amount from a single rule.
        
        Args:
            rule: The IBCommissionRule instance
            volume: The trading volume
            commission_usd: The commission in USD
            
        Returns:
            Decimal value representing the calculated amount
        """
        if rule.calculation_type == 'LOT_BASED':
            amount = rule.value * Decimal(str(volume))
        elif rule.calculation_type == 'PERCENTAGE':
            amount = (rule.value / Decimal('100.0')) * Decimal(str(commission_usd))
        elif rule.calculation_type == 'PIP_VALUE':
            # Implementation for pip value calculation
            amount = Decimal('0.0')
        else:  # TIERED
            amount = Decimal('0.0')
            
        # Apply min/max constraints
        if amount < rule.min_amount:
            amount = rule.min_amount
        elif amount > rule.max_amount:
            amount = rule.max_amount
            
        return amount
    
    @classmethod
    def _find_applicable_rules(cls, ib_id, mt5_account_id, symbol, order_type, customer=None, account=None, **kwargs):
        """
        Find applicable commission rules for a given deal using Django's cache framework
        
        Args:
            ib_id: The IB ID (can be None, will be determined from client mapping)
            mt5_account_id: The MT5 account ID
            symbol: The trading symbol
            order_type: The order type (not used for filtering)
            customer: The customer who made the trade
            account: The account used for the trade
            **kwargs: Additional filters for rules (e.g., commission_type='REBATE')
            
        Returns:
            Dictionary containing:
            - rules: A list of applicable rules
            - client_mapping: The client mapping used to find the rules
        """
        # Import the cache service
        try:
            from shared_models.ib_commission.services.commission_cache_service import CommissionCacheService
            logger.info("Using CommissionCacheService for rule lookups")
        except ImportError:
            logger.warning("CommissionCacheService not available, falling back to database queries")
            CommissionCacheService = None
        
        client_mapping = None
        commission_type = kwargs.get('commission_type')
        account_type_id = account.account_type.id if account and hasattr(account, 'account_type') else None
        
        # If ib_id is provided, we're looking for rules for a specific IB
        if ib_id:
            logger.info(f"Finding rules for specific IB: {ib_id}")
            
            # Get all active agreement memberships for this IB from cache or database
            if CommissionCacheService:
                agreement_members = CommissionCacheService.get_ib_agreements(ib_id)
                logger.info(f"Got {len(agreement_members) if agreement_members else 0} agreement members from cache/DB")
            else:
                agreement_members = IBAgreementMember.objects.filter(
                    customer_id=ib_id,
                    is_active=True
                )
                logger.info(f"Got {agreement_members.count()} agreement members from DB")
            
            if not agreement_members:
                logger.info(f"No active agreements found for IB {ib_id}")
                return {
                    'rules': [],
                    'client_mapping': None
                }
            
            # Find applicable rules for this IB
            for agreement_member in agreement_members:
                # Using caching service
                if CommissionCacheService:
                    # Get all rules for this agreement
                    all_rules = CommissionCacheService.get_commission_rules(
                        agreement_id=agreement_member.agreement_id,
                        symbol=symbol,
                        commission_type=commission_type
                    )
                    
                    logger.info(f"Got {len(all_rules) if all_rules else 0} rules from cache/DB for agreement {agreement_member.agreement_id}")
                    
                    # Rule search order:
                    # 1. Exact symbol + exact account type match
                    # 2. Exact symbol match (any account type)
                    # 3. Any symbol + exact account type match
                    # 4. Wildcard rules (any symbol, any account type)
                    
                    # 1. Exact symbol + exact account type match
                    if account_type_id:
                        exact_symbol_account_type_rules = [
                            rule for rule in all_rules 
                            if rule.symbol and rule.symbol.lower() == symbol.lower() 
                            and rule.account_type_id == account_type_id
                        ]
                        
                        if exact_symbol_account_type_rules:
                            logger.info(f"Found {len(exact_symbol_account_type_rules)} exact symbol and account type rules")
                            # Sort by priority before returning
                            exact_symbol_account_type_rules.sort(key=lambda x: x.priority)
                            return {
                                'rules': exact_symbol_account_type_rules,
                                'client_mapping': None
                            }
                    
                    # 2. Exact symbol match (any account type)
                    exact_symbol_rules = [
                        rule for rule in all_rules 
                        if rule.symbol and rule.symbol.lower() == symbol.lower() 
                        and (rule.account_type_id is None)
                    ]
                    
                    if exact_symbol_rules:
                        logger.info(f"Found {len(exact_symbol_rules)} exact symbol rules")
                        # Sort by priority before returning
                        exact_symbol_rules.sort(key=lambda x: x.priority)
                        return {
                            'rules': exact_symbol_rules,
                            'client_mapping': None
                        }
                    
                    # 3. Any symbol + exact account type match
                    if account_type_id:
                        account_type_rules = [
                            rule for rule in all_rules 
                            if (rule.symbol is None or rule.symbol == '*') 
                            and rule.account_type_id == account_type_id
                        ]
                        
                        if account_type_rules:
                            logger.info(f"Found {len(account_type_rules)} account type rules")
                            # Sort by priority before returning
                            account_type_rules.sort(key=lambda x: x.priority)
                            return {
                                'rules': account_type_rules,
                                'client_mapping': None
                            }
                    
                    # 4. Wildcard rules (any symbol, any account type)
                    wildcard_rules = [
                        rule for rule in all_rules 
                        if (rule.symbol is None or rule.symbol == '*') 
                        and (rule.account_type_id is None)
                    ]
                    
                    if wildcard_rules:
                        logger.info(f"Found {len(wildcard_rules)} wildcard rules")
                        # Sort by priority before returning
                        wildcard_rules.sort(key=lambda x: x.priority)
                        return {
                            'rules': wildcard_rules,
                            'client_mapping': None
                        }
                    
                # Using direct database queries
                else:
                    # 1. Exact symbol + exact account type match
                    if account_type_id:
                        exact_symbol_account_type_rules = IBCommissionRule.objects.filter(
                            agreement_id=agreement_member.agreement_id,
                            symbol__iexact=symbol,
                            account_type_id=account_type_id
                        )
                        
                        # Apply additional filters if provided
                        if kwargs:
                            exact_symbol_account_type_rules = exact_symbol_account_type_rules.filter(**kwargs)
                        
                        # Order by priority
                        exact_symbol_account_type_rules = exact_symbol_account_type_rules.order_by('priority')
                        
                        if exact_symbol_account_type_rules.exists():
                            logger.info(f"Found exact symbol and account type rules for IB {ib_id}")
                            return {
                                'rules': list(exact_symbol_account_type_rules),
                                'client_mapping': None
                            }
                    
                    # 2. Exact symbol match (any account type)
                    exact_symbol_rules = IBCommissionRule.objects.filter(
                        agreement_id=agreement_member.agreement_id,
                        symbol__iexact=symbol,
                        account_type__isnull=True
                    )
                    
                    # Apply additional filters if provided
                    if kwargs:
                        exact_symbol_rules = exact_symbol_rules.filter(**kwargs)
                    
                    # Order by priority
                    exact_symbol_rules = exact_symbol_rules.order_by('priority')
                    
                    if exact_symbol_rules.exists():
                        logger.info(f"Found exact symbol rules for IB {ib_id}")
                        return {
                            'rules': list(exact_symbol_rules),
                            'client_mapping': None
                        }
                    
                    # 3. Any symbol + exact account type match
                    if account_type_id:
                        account_type_rules = IBCommissionRule.objects.filter(
                            agreement_id=agreement_member.agreement_id,
                            account_type_id=account_type_id
                        ).filter(
                            models.Q(symbol='*') | models.Q(symbol__isnull=True)
                        )
                        
                        # Apply additional filters if provided
                        if kwargs:
                            account_type_rules = account_type_rules.filter(**kwargs)
                        
                        # Order by priority
                        account_type_rules = account_type_rules.order_by('priority')
                        
                        if account_type_rules.exists():
                            logger.info(f"Found account type rules for IB {ib_id}")
                            return {
                                'rules': list(account_type_rules),
                                'client_mapping': None
                            }
                    
                    # 4. Wildcard rules (any symbol, any account type)
                    wildcard_rules = IBCommissionRule.objects.filter(
                        agreement_id=agreement_member.agreement_id,
                        account_type__isnull=True
                    ).filter(
                        models.Q(symbol='*') | models.Q(symbol__isnull=True)
                    )
                    
                    # Apply additional filters if provided
                    if kwargs:
                        wildcard_rules = wildcard_rules.filter(**kwargs)
                    
                    # Order by priority
                    wildcard_rules = wildcard_rules.order_by('priority')
                    
                    if wildcard_rules.exists():
                        logger.info(f"Found wildcard rules for IB {ib_id}")
                        return {
                            'rules': list(wildcard_rules),
                            'client_mapping': None
                        }
            
            logger.info(f"No applicable rules found for IB {ib_id}")
            return {
                'rules': [],
                'client_mapping': None
            }
        
        # If ib_id is not provided, we're looking for rules for a client's direct IB
        # Get client mapping from cache or database
        if mt5_account_id and customer:
            if CommissionCacheService:
                client_mapping = CommissionCacheService.get_client_mapping(mt5_account_id, customer.id)
                logger.info(f"Got client mapping from cache/DB for mt5_login={mt5_account_id}, customer_id={customer.id}: {client_mapping is not None}")
            else:
                # PRIORITY 1: Find client mapping with account and mt5_login
                client_mapping = ClientIBMapping.objects.filter(
                    mt5_login=mt5_account_id,
                    customer=customer
                ).first()
                logger.info(f"Got client mapping from DB for mt5_login={mt5_account_id}, customer_id={customer.id}: {client_mapping is not None}")
        
        # PRIORITY 2: If no account-specific mapping, try to find customer mapping
        if not client_mapping and customer:
            if CommissionCacheService:
                client_mapping = CommissionCacheService.get_client_mapping(None, customer.id)
                logger.info(f"Got client mapping from cache/DB for customer_id={customer.id}: {client_mapping is not None}")
            else:
                client_mapping = ClientIBMapping.objects.filter(
                    customer=customer
                ).first()
                logger.info(f"Got client mapping from DB for customer_id={customer.id}: {client_mapping is not None}")
        
        # If no client mapping found, return empty result
        if not client_mapping:
            logger.warning("No client mapping found")
            return {
                'rules': [],
                'client_mapping': None
            }
        
        # Get the IB ID from the client mapping if not provided
        ib_id = client_mapping.direct_ib_customer_id
        logger.info(f"Using IB ID from client mapping: {ib_id}")
        
        # PRIORITY 1: Check for account-specific agreement overrides
        account_agreements = IBAccountAgreement.objects.filter(
            mt5_login=mt5_account_id,
            ib_customer_id=ib_id,
        ).values_list('agreement_id', flat=True)
        logger.info(f"Account-specific agreements: {list(account_agreements)}")
        
        # If account-specific agreements exist, use those
        if account_agreements:
            if CommissionCacheService:
                all_rules = []
                for agreement_id in account_agreements:
                    # Get all rules for this agreement
                    rules = CommissionCacheService.get_commission_rules(
                        agreement_id=agreement_id,
                        symbol=symbol,
                        commission_type=commission_type
                    )
                    
                    logger.info(f"Got {len(rules) if rules else 0} rules from cache/DB for account-specific agreement {agreement_id}")
                    
                    if rules:
                        all_rules.extend(rules)
                
                # Apply the same rule search order as above
                # 1. Exact symbol + exact account type match
                if account_type_id:
                    exact_symbol_account_type_rules = [
                        rule for rule in all_rules 
                        if rule.symbol and rule.symbol.lower() == symbol.lower() 
                        and rule.account_type_id == account_type_id
                    ]
                    
                    if exact_symbol_account_type_rules:
                        logger.info(f"Found {len(exact_symbol_account_type_rules)} exact symbol and account type rules for account-specific agreements")
                        # Sort by priority before returning
                        exact_symbol_account_type_rules.sort(key=lambda x: x.priority)
                        return {
                            'rules': exact_symbol_account_type_rules,
                            'client_mapping': client_mapping
                        }
                
                # 2. Exact symbol match (any account type)
                exact_symbol_rules = [
                    rule for rule in all_rules 
                    if rule.symbol and rule.symbol.lower() == symbol.lower() 
                    and (rule.account_type_id is None)
                ]
                
                if exact_symbol_rules:
                    logger.info(f"Found {len(exact_symbol_rules)} exact symbol rules for account-specific agreements")
                    # Sort by priority before returning
                    exact_symbol_rules.sort(key=lambda x: x.priority)
                    return {
                        'rules': exact_symbol_rules,
                        'client_mapping': client_mapping
                    }
                
                # 3. Any symbol + exact account type match
                if account_type_id:
                    account_type_rules = [
                        rule for rule in all_rules 
                        if (rule.symbol is None or rule.symbol == '*') 
                        and rule.account_type_id == account_type_id
                    ]
                    
                    if account_type_rules:
                        logger.info(f"Found {len(account_type_rules)} account type rules for account-specific agreements")
                        # Sort by priority before returning
                        account_type_rules.sort(key=lambda x: x.priority)
                        return {
                            'rules': account_type_rules,
                            'client_mapping': client_mapping
                        }
                
                # 4. Wildcard rules (any symbol, any account type)
                wildcard_rules = [
                    rule for rule in all_rules 
                    if (rule.symbol is None or rule.symbol == '*') 
                    and (rule.account_type_id is None)
                ]
                
                if wildcard_rules:
                    logger.info(f"Found {len(wildcard_rules)} wildcard rules for account-specific agreements")
                    # Sort by priority before returning
                    wildcard_rules.sort(key=lambda x: x.priority)
                    return {
                        'rules': wildcard_rules,
                        'client_mapping': client_mapping
                    }
            else:
                # Direct database queries with the same rule search order
                # 1. Exact symbol + exact account type match
                if account_type_id:
                    exact_rules = IBCommissionRule.objects.filter(
                        agreement_id__in=account_agreements,
                        symbol__iexact=symbol,
                        account_type_id=account_type_id
                    )
                    
                    # Apply additional filters if provided
                    if kwargs:
                        exact_rules = exact_rules.filter(**kwargs)
                    
                    # Order by priority
                    exact_rules = exact_rules.order_by('priority')
                    
                    if exact_rules.exists():
                        logger.info(f"Found exact symbol and account type rules for account-specific agreements")
                        return {
                            'rules': list(exact_rules),
                            'client_mapping': client_mapping
                        }
                
                # 2. Exact symbol match (any account type)
                exact_symbol_rules = IBCommissionRule.objects.filter(
                    agreement_id__in=account_agreements,
                    symbol__iexact=symbol,
                    account_type__isnull=True
                )
                
                # Apply additional filters if provided
                if kwargs:
                    exact_symbol_rules = exact_symbol_rules.filter(**kwargs)
                
                # Order by priority
                exact_symbol_rules = exact_symbol_rules.order_by('priority')
                
                if exact_symbol_rules.exists():
                    logger.info(f"Found exact symbol rules for account-specific agreements")
                    return {
                        'rules': list(exact_symbol_rules),
                        'client_mapping': client_mapping
                    }
                
                # 3. Any symbol + exact account type match
                if account_type_id:
                    account_type_rules = IBCommissionRule.objects.filter(
                        agreement_id__in=account_agreements,
                        account_type_id=account_type_id
                    ).filter(
                        models.Q(symbol='*') | models.Q(symbol__isnull=True)
                    )
                    
                    # Apply additional filters if provided
                    if kwargs:
                        account_type_rules = account_type_rules.filter(**kwargs)
                    
                    # Order by priority
                    account_type_rules = account_type_rules.order_by('priority')
                    
                    if account_type_rules.exists():
                        logger.info(f"Found account type rules for account-specific agreements")
                        return {
                            'rules': list(account_type_rules),
                            'client_mapping': client_mapping
                        }
                
                # 4. Wildcard rules (any symbol, any account type)
                wildcard_rules = IBCommissionRule.objects.filter(
                    agreement_id__in=account_agreements,
                    account_type__isnull=True
                ).filter(
                    models.Q(symbol='*') | models.Q(symbol__isnull=True)
                )
                
                # Apply additional filters if provided
                if kwargs:
                    wildcard_rules = wildcard_rules.filter(**kwargs)
                
                # Order by priority
                wildcard_rules = wildcard_rules.order_by('priority')
                
                if wildcard_rules.exists():
                    logger.info(f"Found wildcard rules for account-specific agreements")
                    return {
                        'rules': list(wildcard_rules),
                        'client_mapping': client_mapping
                    }
        
        logger.info(f"Client mapping agreement: {client_mapping.agreement}")
        logger.info(f"Client mapping agreement ID: {client_mapping.agreement.id if client_mapping.agreement else 'None'}")
        logger.info(f"Client mapping agreement_id: {client_mapping.agreement_id}")
        
        # If client mapping exists and has a specific agreement, use that
        if client_mapping and client_mapping.agreement_id:
            if CommissionCacheService:
                # Get all rules for this agreement
                all_rules = CommissionCacheService.get_commission_rules(
                    agreement_id=client_mapping.agreement_id,
                    symbol=symbol,
                    commission_type=commission_type
                )
                
                logger.info(f"Got {len(all_rules) if all_rules else 0} rules from cache/DB for client mapping agreement {client_mapping.agreement_id}")
                
                # Apply the same rule search order as above
                # 1. Exact symbol + exact account type match
                if account_type_id:
                    exact_symbol_account_type_rules = [
                        rule for rule in all_rules 
                        if rule.symbol and rule.symbol.lower() == symbol.lower() 
                        and rule.account_type_id == account_type_id
                    ]
                    
                    if exact_symbol_account_type_rules:
                        logger.info(f"Found {len(exact_symbol_account_type_rules)} exact symbol and account type rules for client mapping agreement")
                        # Sort by priority before returning
                        exact_symbol_account_type_rules.sort(key=lambda x: x.priority)
                        return {
                            'rules': exact_symbol_account_type_rules,
                            'client_mapping': client_mapping
                        }
                
                # 2. Exact symbol match (any account type)
                exact_symbol_rules = [
                    rule for rule in all_rules 
                    if rule.symbol and rule.symbol.lower() == symbol.lower() 
                    and (rule.account_type_id is None)
                ]
                
                if exact_symbol_rules:
                    logger.info(f"Found {len(exact_symbol_rules)} exact symbol rules for client mapping agreement")
                    # Sort by priority before returning
                    exact_symbol_rules.sort(key=lambda x: x.priority)
                    return {
                        'rules': exact_symbol_rules,
                        'client_mapping': client_mapping
                    }
                
                # 3. Any symbol + exact account type match
                if account_type_id:
                    account_type_rules = [
                        rule for rule in all_rules 
                        if (rule.symbol is None or rule.symbol == '*') 
                        and rule.account_type_id == account_type_id
                    ]
                    
                    if account_type_rules:
                        logger.info(f"Found {len(account_type_rules)} account type rules for client mapping agreement")
                        # Sort by priority before returning
                        account_type_rules.sort(key=lambda x: x.priority)
                        return {
                            'rules': account_type_rules,
                            'client_mapping': client_mapping
                        }
                
                # 4. Wildcard rules (any symbol, any account type)
                wildcard_rules = [
                    rule for rule in all_rules 
                    if (rule.symbol is None or rule.symbol == '*') 
                    and (rule.account_type_id is None)
                ]
                
                if wildcard_rules:
                    logger.info(f"Found {len(wildcard_rules)} wildcard rules for client mapping agreement")
                    # Sort by priority before returning
                    wildcard_rules.sort(key=lambda x: x.priority)
                    return {
                        'rules': wildcard_rules,
                        'client_mapping': client_mapping
                    }
                
                return {
                    'rules': [],
                    'client_mapping': client_mapping
                }
            else:
                # Direct database queries with the same rule search order
                # 1. Exact symbol + exact account type match
                if account_type_id:
                    exact_rules = IBCommissionRule.objects.filter(
                        agreement_id=client_mapping.agreement_id,
                        symbol__iexact=symbol,
                        account_type_id=account_type_id
                    )
                    
                    # Apply additional filters if provided
                    if kwargs:
                        exact_rules = exact_rules.filter(**kwargs)
                    
                    # Order by priority
                    exact_rules = exact_rules.order_by('priority')
                    
                    if exact_rules.exists():
                        logger.info(f"Found exact symbol and account type rules for client mapping agreement")
                        return {
                            'rules': list(exact_rules),
                            'client_mapping': client_mapping
                        }
                
                # 2. Exact symbol match (any account type)
                exact_symbol_rules = IBCommissionRule.objects.filter(
                    agreement_id=client_mapping.agreement_id,
                    symbol__iexact=symbol,
                    account_type__isnull=True
                )
                
                # Apply additional filters if provided
                if kwargs:
                    exact_symbol_rules = exact_symbol_rules.filter(**kwargs)
                
                # Order by priority
                exact_symbol_rules = exact_symbol_rules.order_by('priority')
                
                if exact_symbol_rules.exists():
                    logger.info(f"Found exact symbol rules for client mapping agreement")
                    return {
                        'rules': list(exact_symbol_rules),
                        'client_mapping': client_mapping
                    }
                
                # 3. Any symbol + exact account type match
                if account_type_id:
                    account_type_rules = IBCommissionRule.objects.filter(
                        agreement_id=client_mapping.agreement_id,
                        account_type_id=account_type_id
                    ).filter(
                        models.Q(symbol='*') | models.Q(symbol__isnull=True)
                    )
                    
                    # Apply additional filters if provided
                    if kwargs:
                        account_type_rules = account_type_rules.filter(**kwargs)
                    
                    # Order by priority
                    account_type_rules = account_type_rules.order_by('priority')
                    
                    if account_type_rules.exists():
                        logger.info(f"Found account type rules for client mapping agreement")
                        return {
                            'rules': list(account_type_rules),
                            'client_mapping': client_mapping
                        }
                
                # 4. Wildcard rules (any symbol, any account type)
                wildcard_rules = IBCommissionRule.objects.filter(
                    agreement_id=client_mapping.agreement_id,
                    account_type__isnull=True
                ).filter(
                    models.Q(symbol='*') | models.Q(symbol__isnull=True)
                )
                
                # Apply additional filters if provided
                if kwargs:
                    wildcard_rules = wildcard_rules.filter(**kwargs)
                
                # Order by priority
                wildcard_rules = wildcard_rules.order_by('priority')
                
                if wildcard_rules.exists():
                    logger.info(f"Found wildcard rules for client mapping agreement")
                    return {
                        'rules': list(wildcard_rules),
                        'client_mapping': client_mapping
                    }
                
                logger.info(f"No applicable rules found for agreement {client_mapping.agreement_id}")
                
                return {
                    'rules': [],
                    'client_mapping': client_mapping
                }
        
        # If we get here, no applicable rules were found
        logger.info("No applicable rules were found")
        return {
            'rules': [],
            'client_mapping': client_mapping
        }
    
    @classmethod
    def _calculate_client_deduction(cls, distributions):
        """
        Calculate the total amount to deduct from the client.
        
        Args:
            distributions: List of CommissionDistribution objects
            
        Returns:
            Decimal value of total client deduction
        """
        # Sum up all commission distributions (not rebates)
        return sum(
            d.amount for d in distributions 
            if d.distribution_type == cls.COMMISSION_TYPE
        )
    
    @classmethod
    def _create_transactions(cls, distributions, deal_data, customer):
        """
        Create CommissionRebateTransaction records for distributions.
        
        Args:
            distributions: List of CommissionDistribution objects
            deal_data: Original MT5 deal data
            customer: Customer model instance
            
        Returns:
            List of created transaction records
        """
        transactions = []
        
        with transaction.atomic():
            for dist in distributions:
                # Create transaction record
                tx = CommissionRebateTransaction.objects.create(
                    ib_account=dist.ib_account,
                    account=dist.ib_account,
                    amount=dist.amount,
                    customer=customer,
                    transaction_type=dist.distribution_type,
                    status='APPROVED',
                    calculation_basis={
                        'deal_ticket': dist.deal_ticket_id,
                        'distribution_id': dist.id,
                        'rule_id': dist.rule_id,
                        'mt5_data': deal_data
                    }
                )
                transactions.append(tx)
                
                # Update distribution with transaction reference and mark as processed
                dist.transaction = tx
                dist.is_processed = True
                dist.processing_status = 'PROCESSED'
                dist.processing_notes = 'Successfully processed and transaction created'
                dist.save()
        
        return transactions
    
    @classmethod
    def _create_distribution_from_rule(cls, deal_ticket, rule, client_id, ib_id, volume, commission_usd):
        """
        Create a commission distribution based on a rule.
        
        Args:
            deal_ticket: The deal ticket ID
            rule: The IBCommissionRule instance
            client_id: The client ID
            ib_id: The IB ID
            volume: The trading volume
            commission_usd: The commission in USD
            
        Returns:
            The created CommissionDistribution instance
        """
        # Calculate amount based on rule type
        amount = Decimal('0.0')
        
        if rule.calculation_method == 'fixed':
            amount = rule.value
        elif rule.calculation_method == 'percentage':
            amount = (rule.value / Decimal('100.0')) * Decimal(str(commission_usd))
        elif rule.calculation_method == 'per_lot':
            amount = rule.value * Decimal(str(volume))
        
        # Determine distribution type
        distribution_type = cls.REBATE_TYPE if rule.is_rebate else cls.COMMISSION_TYPE
        
        # Create the distribution
        if amount > Decimal('0.0'):
            return CommissionDistribution.objects.create(
                deal_ticket=deal_ticket,
                customer_id=ib_id,
                client_customer_id=client_id,
                distribution_type=distribution_type,
                amount=amount,
                rule=rule,
                is_processed=False,
                processed_time=datetime.now()
            )
        
        return None 