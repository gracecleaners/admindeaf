"""
Finance API Views
Handles wallet balance, payments, and transactions
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum, Q
from django.db import transaction as db_transaction
from decimal import Decimal
import logging

from .models import Ledger, Payments, PaymentMethods, UserWallet
from accounts.models import User

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def wallet_balance(request):
    """Get current wallet balance for authenticated user"""
    try:
        user = request.user
        
        # Calculate balance from ledger
        # credits = Ledger.objects.filter(
        #     user_to=user,
        #     is_credit=True,
        #     is_valid=True
        # ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        # debits = Ledger.objects.filter(
        #     user_from=user,
        #     is_debit=True,
        #     is_valid=True
        # ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        # balance = float(credits - debits)

        wallet, created = UserWallet.objects.get_or_create(
            owner=user,
            defaults={
                'amount': Decimal('0.00'),
                'points': Decimal('0.00'),
                'is_active': True,
            }
        )
        # If the wallet was just created, ensure all required fields are set (for legacy DBs)
        updated = False
        if wallet.amount is None:
            wallet.amount = Decimal('0.00')
            updated = True
        if wallet.points is None:
            wallet.points = Decimal('0.00')
            updated = True
        if wallet.is_active is None:
            wallet.is_active = True
            updated = True
        if updated:
            wallet.save()
            
        balance = wallet.amount
        
        return Response({
            'success': True,
            'balance': balance,
            'currency': 'UGX'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error fetching wallet balance: {str(e)}")
        return Response({
            'success': False,
            'error': 'Could not fetch balance'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def wallet_topup(request):
    """Initialize wallet top-up transaction"""
    try:
        user = request.user
        amount = request.data.get('amount')
        payment_method = request.data.get('payment_method', 'mobile_money')
        
        if not amount:
            return Response({
                'success': False,
                'error': 'Amount is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        amount = Decimal(str(amount))
        
        if amount < 1000:
            return Response({
                'success': False,
                'error': 'Minimum top-up amount is UGX 1,000'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get or create payment method
        payment_method_obj, _ = PaymentMethods.objects.get_or_create(
            name=payment_method.replace('_', ' ').title(),
            defaults={'is_active': True}
        )
        
        with db_transaction.atomic():
            # Create payment record
            payment = Payments.objects.create(
                method=payment_method_obj,
                amount=amount,
                phone=str(user.phone_number),
                note=f"Wallet top-up by {user.username}",
                is_verified=False,
                is_successful=False
            )
            
            # In production, integrate with actual payment gateway
            # For now, simulate payment initiation
            
            return Response({
                'success': True,
                'message': 'Payment initiated',
                'payment_id': payment.id,
                'amount': float(amount),
                'instructions': f'Complete payment on your {payment_method.replace("_", " ")} device'
            }, status=status.HTTP_201_CREATED)
            
    except Exception as e:
        logger.error(f"Error processing top-up: {str(e)}")
        return Response({
            'success': False,
            'error': 'Top-up failed. Please try again.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def deduct_ride_payment(request):
    """Deduct payment from user wallet for ride"""
    try:
        user = request.user
        amount = request.data.get('amount')
        ride_id = request.data.get('ride_id')
        
        if not amount:
            return Response({
                'success': False,
                'error': 'Amount is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        amount = Decimal(str(amount))
        
        # Check balance
        credits = Ledger.objects.filter(
            user_to=user,
            is_credit=True,
            is_valid=True
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        debits = Ledger.objects.filter(
            user_from=user,
            is_debit=True,
            is_valid=True
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        balance = credits - debits
        
        if balance < amount:
            return Response({
                'success': False,
                'error': 'Insufficient balance',
                'balance': float(balance),
                'required': float(amount)
            }, status=status.HTTP_400_BAD_REQUEST)
        
        with db_transaction.atomic():
            # Create debit ledger entry
            Ledger.objects.create(
                user_from=user,
                amount=amount,
                is_debit=True,
                is_valid=True,
                notes=f"Payment for ride #{ride_id}"
            )
            
            return Response({
                'success': True,
                'message': 'Payment deducted successfully',
                'new_balance': float(balance - amount)
            }, status=status.HTTP_200_OK)
            
    except Exception as e:
        logger.error(f"Error deducting payment: {str(e)}")
        return Response({
            'success': False,
            'error': 'Payment deduction failed'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def transaction_history(request):
    """Get user's transaction history"""
    try:
        user = request.user
        limit = int(request.query_params.get('limit', 10))
        
        # Get recent transactions
        transactions = []
        
        # Credits
        credits = Ledger.objects.filter(
            user_to=user,
            is_credit=True,
            is_valid=True
        ).order_by('-timestamp')[:limit]
        
        for ledger in credits:
            transactions.append({
                'id': str(ledger.transaction_id),
                'type': 'credit',
                'amount': float(ledger.amount),
                'notes': ledger.notes or 'Wallet top-up',
                'timestamp': ledger.timestamp.isoformat()
            })
        
        # Debits
        debits = Ledger.objects.filter(
            user_from=user,
            is_debit=True,
            is_valid=True
        ).order_by('-timestamp')[:limit]
        
        for ledger in debits:
            transactions.append({
                'id': str(ledger.transaction_id),
                'type': 'debit',
                'amount': float(ledger.amount),
                'notes': ledger.notes or 'Payment',
                'timestamp': ledger.timestamp.isoformat()
            })
        
        # Sort by timestamp
        transactions.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return Response({
            'success': True,
            'transactions': transactions[:limit]
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error fetching transactions: {str(e)}")
        return Response({
            'success': False,
            'error': 'Could not fetch transactions'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

