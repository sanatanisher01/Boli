from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.utils import timezone
from .models import UserProfile, Product, Bid
import json

@csrf_exempt
def verify_user(request):
    """Verify user by unique_id"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            unique_id = data.get('user_id')
            
            profile = UserProfile.objects.get(unique_id=unique_id)
            return JsonResponse({
                'success': True,
                'user': {
                    'id': profile.user.id,
                    'username': profile.user.username,
                    'name': profile.user.get_full_name() or profile.user.username,
                    'unique_id': profile.unique_id
                }
            })
        except UserProfile.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Invalid user ID'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'})

@csrf_exempt
def get_active_bids(request):
    """Get user's active bids"""
    unique_id = request.GET.get('user_id')
    
    try:
        profile = UserProfile.objects.get(unique_id=unique_id)
        user = profile.user
        
        active_bids = Bid.objects.filter(
            bidder=user,
            product__is_active=True,
            product__end_time__gt=timezone.now()
        ).select_related('product')
        
        bids_data = []
        for bid in active_bids:
            is_winning = bid.amount == bid.product.current_highest_bid
            time_left = bid.product.end_time - timezone.now()
            
            bids_data.append({
                'auction_id': bid.product.id,
                'product_name': bid.product.title,
                'your_bid': float(bid.amount),
                'current_highest': float(bid.product.current_highest_bid),
                'is_winning': is_winning,
                'time_remaining_seconds': time_left.total_seconds(),
                'time_remaining_formatted': format_time_remaining(time_left)
            })
        
        return JsonResponse({'success': True, 'bids': bids_data})
    except UserProfile.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Invalid user ID'})

@csrf_exempt
def get_auction_details(request):
    """Get auction details"""
    auction_id = request.GET.get('auction_id')
    
    try:
        product = Product.objects.get(id=auction_id, is_active=True)
        time_left = product.end_time - timezone.now()
        
        return JsonResponse({
            'success': True,
            'auction': {
                'id': product.id,
                'title': product.title,
                'description': product.description,
                'current_bid': float(product.current_highest_bid),
                'base_price': float(product.base_price),
                'time_remaining_seconds': time_left.total_seconds(),
                'time_remaining_formatted': format_time_remaining(time_left),
                'total_bids': product.bids.count(),
                'image_url': product.image.url if product.image else None
            }
        })
    except Product.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Auction not found'})

@csrf_exempt
def place_bid(request):
    """Place a new bid"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            unique_id = data.get('user_id')
            auction_id = data.get('auction_id')
            bid_amount = float(data.get('bid_amount'))
            
            profile = UserProfile.objects.get(unique_id=unique_id)
            product = Product.objects.get(id=auction_id, is_active=True)
            
            if product.end_time <= timezone.now():
                return JsonResponse({'success': False, 'error': 'Auction has ended'})
            
            if bid_amount <= product.current_highest_bid:
                return JsonResponse({
                    'success': False, 
                    'error': f'Bid must be higher than current bid of ${product.current_highest_bid}'
                })
            
            bid = Bid.objects.create(
                product=product,
                bidder=profile.user,
                amount=bid_amount
            )
            
            return JsonResponse({
                'success': True,
                'message': f'Bid of ${bid_amount} placed successfully!',
                'new_highest_bid': float(bid_amount)
            })
            
        except UserProfile.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Invalid user ID'})
        except Product.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Auction not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'})

@csrf_exempt
def get_bid_history(request):
    """Get user's bid history"""
    unique_id = request.GET.get('user_id')
    limit = int(request.GET.get('limit', 10))
    
    try:
        profile = UserProfile.objects.get(unique_id=unique_id)
        user = profile.user
        
        bids = Bid.objects.filter(bidder=user).select_related('product').order_by('-timestamp')[:limit]
        
        history_data = []
        for bid in bids:
            is_winning = bid.amount == bid.product.current_highest_bid
            status = 'Won' if bid.product.is_expired and is_winning else 'Active' if not bid.product.is_expired else 'Lost'
            
            history_data.append({
                'auction_id': bid.product.id,
                'product_name': bid.product.title,
                'bid_amount': float(bid.amount),
                'timestamp': bid.timestamp.isoformat(),
                'status': status,
                'is_winning': is_winning
            })
        
        return JsonResponse({'success': True, 'history': history_data})
    except UserProfile.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Invalid user ID'})

@csrf_exempt
def get_auction_status(request):
    """Get real-time auction status"""
    auction_ids = request.GET.get('auction_ids', '').split(',')
    
    try:
        products = Product.objects.filter(id__in=auction_ids, is_active=True)
        
        status_data = []
        for product in products:
            time_left = product.end_time - timezone.now()
            
            status_data.append({
                'auction_id': product.id,
                'title': product.title,
                'current_bid': float(product.current_highest_bid),
                'time_remaining_seconds': time_left.total_seconds(),
                'time_remaining_formatted': format_time_remaining(time_left),
                'total_bids': product.bids.count(),
                'is_active': time_left.total_seconds() > 0
            })
        
        return JsonResponse({'success': True, 'auctions': status_data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

def format_time_remaining(time_delta):
    """Format time remaining in human readable format"""
    if time_delta.total_seconds() <= 0:
        return "Auction ended"
    
    days = time_delta.days
    hours, remainder = divmod(time_delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    if days > 0:
        return f"{days} days, {hours} hours"
    elif hours > 0:
        return f"{hours} hours, {minutes} minutes"
    else:
        return f"{minutes} minutes, {seconds} seconds"