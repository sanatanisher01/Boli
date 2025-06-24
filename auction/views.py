from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.db.models import Max
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import csv
import json
import uuid
from .models import Product, Bid, UserProfile
from .forms import CustomUserCreationForm, ProductForm, BidForm, UserProfileForm

def home(request):
    products = Product.objects.filter(is_active=True, end_time__gt=timezone.now())
    return render(request, 'auction/home.html', {'products': products})

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            
            # Create user profile
            profile = UserProfile.objects.create(user=user)
            
            # Send verification email
            send_verification_email(user, profile.activation_token)
            
            messages.success(request, 'Registration successful! Please check your email to verify your account.')
            return redirect('email_sent')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def send_verification_email(user, token):
    subject = 'Welcome to BoliBazaar - Verify Your Account'
    html_message = render_to_string('emails/verification_email.html', {
        'user': user,
        'token': token,
        'domain': 'localhost:8000'
    })
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=html_message,
        fail_silently=False,
    )

def send_welcome_email(user):
    subject = 'Welcome to BoliBazaar - Start Bidding!'
    html_message = render_to_string('emails/welcome_email.html', {
        'user': user,
    })
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=html_message,
        fail_silently=False,
    )

def send_bid_confirmation_email(user, product, bid_amount, is_highest, current_highest):
    subject = f'Bid Placed Successfully - {product.title}'
    html_message = render_to_string('emails/bid_confirmation.html', {
        'user': user,
        'product': product,
        'bid_amount': bid_amount,
        'is_highest': is_highest,
        'current_highest': current_highest,
    })
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=html_message,
        fail_silently=False,
    )

def send_auction_result_emails(product):
    """Send win/loss emails when auction ends"""
    if not product.is_expired:
        return
    
    winner = product.highest_bidder
    winning_bid = product.current_highest_bid
    all_bidders = User.objects.filter(bids__product=product).distinct()
    
    for bidder in all_bidders:
        user_highest_bid = bidder.bids.filter(product=product).order_by('-amount').first()
        
        if bidder == winner:
            # Send winner email
            subject = f'🏆 Congratulations! You Won - {product.title}'
            html_message = render_to_string('emails/auction_won.html', {
                'user': bidder,
                'product': product,
                'winning_bid': winning_bid,
                'total_bids': product.bids.count(),
            })
        else:
            # Send loser email
            subject = f'Auction Ended - {product.title}'
            html_message = render_to_string('emails/auction_lost.html', {
                'user': bidder,
                'product': product,
                'user_highest_bid': user_highest_bid.amount if user_highest_bid else 0,
                'winning_bid': winning_bid,
                'winner_name': winner.get_full_name() if winner else 'Unknown',
            })
        
        plain_message = strip_tags(html_message)
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [bidder.email],
            html_message=html_message,
            fail_silently=True,
        )

# OmniDimension API Views
@csrf_exempt
def api_active_auctions(request):
    products = Product.objects.filter(
        is_active=True,
        start_time__lte=timezone.now(),
        end_time__gt=timezone.now()
    )
    
    auctions = []
    for product in products:
        auctions.append({
            'id': product.id,
            'title': product.title,
            'current_bid': float(product.current_highest_bid),
            'time_remaining': (product.end_time - timezone.now()).total_seconds(),
            'total_bids': product.bids.count()
        })
    
    return JsonResponse(auctions, safe=False)

@csrf_exempt
def api_product_status(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return JsonResponse({
        'product_name': product.title,
        'current_bid': float(product.current_highest_bid),
        'time_remaining': (product.end_time - timezone.now()).total_seconds(),
        'is_active': product.can_bid,
        'total_bids': product.bids.count()
    })

@csrf_exempt
def api_time_remaining(request, pk):
    product = get_object_or_404(Product, pk=pk)
    time_left = product.end_time - timezone.now()
    
    if time_left.total_seconds() <= 0:
        formatted_time = "Auction ended"
    else:
        days = time_left.days
        hours, remainder = divmod(time_left.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if days > 0:
            formatted_time = f"{days} days, {hours} hours"
        elif hours > 0:
            formatted_time = f"{hours} hours, {minutes} minutes"
        else:
            formatted_time = f"{minutes} minutes, {seconds} seconds"
    
    return JsonResponse({
        'product_name': product.title,
        'time_remaining_seconds': time_left.total_seconds(),
        'time_remaining_formatted': formatted_time
    })

@csrf_exempt
def api_bid_history(request, pk):
    product = get_object_or_404(Product, pk=pk)
    bids = product.bids.all()[:20]
    
    bid_data = []
    for bid in bids:
        bid_data.append({
            'bidder': bid.bidder.get_full_name() or bid.bidder.username,
            'amount': float(bid.amount),
            'timestamp': bid.timestamp.isoformat()
        })
    
    return JsonResponse({
        'product_name': product.title,
        'total_bids': product.bids.count(),
        'bids': bid_data
    })

@csrf_exempt
def api_search_product(request):
    name = request.GET.get('name', '')
    if name:
        product = Product.objects.filter(
            title__icontains=name,
            is_active=True
        ).first()
        
        if product:
            return JsonResponse({'product_id': product.id})
    
    return JsonResponse({'product_id': None})

@csrf_exempt
def omnidimension_webhook(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            event_type = data.get('event_type')
            
            if event_type == 'command_processed':
                return JsonResponse({'status': 'success'})
            
            return JsonResponse({'status': 'success'})
            
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'})
    
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'})

# OmniDimension Voice Agent APIs
@csrf_exempt
def voice_navigate(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        destination = data.get('destination', '').lower()
        
        url_map = {
            'home': '/',
            'login': '/login/',
            'register': '/register/',
            'dashboard': '/dashboard/',
            'admin': '/admin-dashboard/',
            'profile': '/profile/'
        }
        
        url = url_map.get(destination)
        if url:
            return JsonResponse({
                'success': True,
                'action': 'navigate',
                'url': url,
                'message': f'Navigating to {destination} page'
            })
        
        return JsonResponse({'success': False, 'message': 'Invalid destination'})
    return JsonResponse({'success': False, 'message': 'Method not allowed'})

@csrf_exempt
def voice_authenticate(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        action = data.get('action')
        
        if action == 'demo_login':
            return JsonResponse({
                'success': True,
                'action': 'auto_login',
                'username': 'demo',
                'password': 'demo123',
                'message': 'Logging in as demo user'
            })
        elif action == 'admin_login':
            return JsonResponse({
                'success': True,
                'action': 'auto_login',
                'username': 'admin',
                'password': 'admin123',
                'message': 'Logging in as admin'
            })
        elif action == 'logout':
            return JsonResponse({
                'success': True,
                'action': 'logout',
                'url': '/logout/',
                'message': 'Logging out'
            })
        
        return JsonResponse({'success': False, 'message': 'Invalid authentication action'})
    return JsonResponse({'success': False, 'message': 'Method not allowed'})

@csrf_exempt
def voice_product_search(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        query = data.get('query', '')
        
        if query:
            products = Product.objects.filter(
                title__icontains=query,
                is_active=True
            )[:5]
            
            results = []
            for product in products:
                results.append({
                    'id': product.id,
                    'title': product.title,
                    'current_bid': float(product.current_highest_bid),
                    'url': f'/product/{product.id}/'
                })
            
            return JsonResponse({
                'success': True,
                'products': results,
                'message': f'Found {len(results)} products matching "{query}"'
            })
        
        # Show all products
        products = Product.objects.filter(is_active=True)[:10]
        results = []
        for product in products:
            results.append({
                'id': product.id,
                'title': product.title,
                'current_bid': float(product.current_highest_bid),
                'url': f'/product/{product.id}/'
            })
        
        return JsonResponse({
            'success': True,
            'products': results,
            'message': f'Showing {len(results)} active auctions'
        })
    return JsonResponse({'success': False, 'message': 'Method not allowed'})

@csrf_exempt
def voice_place_bid(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        amount = data.get('amount')
        product_id = data.get('product_id')
        
        if not request.user.is_authenticated:
            return JsonResponse({
                'success': False,
                'message': 'Please login first to place bids'
            })
        
        try:
            product = Product.objects.get(id=product_id)
            
            if not product.can_bid:
                return JsonResponse({
                    'success': False,
                    'message': 'Bidding is not available for this product'
                })
            
            if amount <= product.current_highest_bid:
                return JsonResponse({
                    'success': False,
                    'message': f'Bid must be higher than current bid of {product.current_highest_bid} rupees'
                })
            
            bid = Bid.objects.create(
                product=product,
                bidder=request.user,
                amount=amount
            )
            
            return JsonResponse({
                'success': True,
                'message': f'Bid of {amount} rupees placed successfully',
                'new_highest_bid': float(amount)
            })
            
        except Product.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Product not found'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': 'Error placing bid'
            })
    return JsonResponse({'success': False, 'message': 'Method not allowed'})

@csrf_exempt
def voice_get_bid_info(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        product_id = data.get('product_id')
        info_type = data.get('type', 'current')
        
        try:
            product = Product.objects.get(id=product_id)
            
            if info_type == 'current':
                return JsonResponse({
                    'success': True,
                    'product_name': product.title,
                    'current_bid': float(product.current_highest_bid),
                    'total_bids': product.bids.count(),
                    'message': f'Current highest bid for {product.title} is {product.current_highest_bid} rupees'
                })
            
            elif info_type == 'history':
                bids = product.bids.all()[:10]
                bid_list = []
                for bid in bids:
                    bid_list.append({
                        'bidder': bid.bidder.username,
                        'amount': float(bid.amount),
                        'time': bid.timestamp.strftime('%H:%M')
                    })
                
                return JsonResponse({
                    'success': True,
                    'product_name': product.title,
                    'bids': bid_list,
                    'message': f'Showing recent bid history for {product.title}'
                })
            
        except Product.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Product not found'
            })
    return JsonResponse({'success': False, 'message': 'Method not allowed'})

@csrf_exempt
def voice_admin_action(request):
    if request.method == 'POST':
        if not request.user.is_staff:
            return JsonResponse({
                'success': False,
                'message': 'Admin access required'
            })
        
        data = json.loads(request.body)
        action = data.get('action')
        
        action_map = {
            'add_product': '/add-product/',
            'manage_products': '/admin-dashboard/',
            'generate_report': '/generate-report/',
            'view_bids': '/admin-dashboard/'
        }
        
        url = action_map.get(action)
        if url:
            return JsonResponse({
                'success': True,
                'action': 'navigate',
                'url': url,
                'message': f'Opening {action.replace("_", " ")} page'
            })
        
        return JsonResponse({'success': False, 'message': 'Invalid admin action'})
    return JsonResponse({'success': False, 'message': 'Method not allowed'})

@csrf_exempt
def voice_form_action(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        action = data.get('action')
        form_data = data.get('form_data', {})
        
        if action == 'fill_registration':
            return JsonResponse({
                'success': True,
                'action': 'fill_form',
                'form_type': 'registration',
                'data': form_data,
                'message': 'Filling registration form'
            })
        elif action == 'submit_form':
            return JsonResponse({
                'success': True,
                'action': 'submit_form',
                'message': 'Submitting form'
            })
        elif action == 'clear_form':
            return JsonResponse({
                'success': True,
                'action': 'clear_form',
                'message': 'Clearing form fields'
            })
        
        return JsonResponse({'success': False, 'message': 'Invalid form action'})
    return JsonResponse({'success': False, 'message': 'Method not allowed'})

@csrf_exempt
def voice_theme_toggle(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        theme = data.get('theme', 'toggle')
        
        return JsonResponse({
            'success': True,
            'action': 'theme_change',
            'theme': theme,
            'message': f'Switching to {theme} mode'
        })
    return JsonResponse({'success': False, 'message': 'Method not allowed'})

@csrf_exempt
def voice_help(request):
    if request.method == 'POST':
        commands = {
            'navigation': [
                'Go to home page',
                'Open login page',
                'Show my dashboard',
                'Open admin panel'
            ],
            'bidding': [
                'Place bid of [amount] rupees',
                'What is the current bid?',
                'Show bid history',
                'Check my bids'
            ],
            'products': [
                'Show all products',
                'Search for [product name]',
                'Open product details'
            ],
            'admin': [
                'Add new product',
                'Manage products',
                'Generate report'
            ]
        }
        
        return JsonResponse({
            'success': True,
            'commands': commands,
            'message': 'Here are the available voice commands'
        })
    return JsonResponse({'success': False, 'message': 'Method not allowed'})

def verify_email(request, token):
    try:
        profile = UserProfile.objects.get(activation_token=token)
        if not profile.is_email_verified:
            profile.is_email_verified = True
            profile.user.is_active = True
            profile.save()
            profile.user.save()
            
            # Send welcome email
            send_welcome_email(profile.user)
            
            messages.success(request, 'Email verified successfully! You can now start bidding.')
            return redirect('login')
        else:
            messages.info(request, 'Email already verified.')
            return redirect('login')
    except UserProfile.DoesNotExist:
        messages.error(request, 'Invalid verification link.')
        return redirect('register')

def email_sent(request):
    return render(request, 'registration/email_sent.html')

@login_required
def profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile)
    
    return render(request, 'auction/profile.html', {'form': form, 'profile': profile})

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            # Generate reset token
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.activation_token = uuid.uuid4()
            profile.save()
            
            # Send reset email
            send_password_reset_email(user, profile.activation_token)
            messages.success(request, 'Password reset link sent to your email!')
            return redirect('login')
        except User.DoesNotExist:
            messages.error(request, 'No account found with this email address.')
    
    return render(request, 'registration/forgot_password.html')

def reset_password(request, token):
    try:
        profile = UserProfile.objects.get(activation_token=token)
        user = profile.user
        
        if request.method == 'POST':
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            
            if password == confirm_password and len(password) >= 8:
                user.set_password(password)
                user.save()
                profile.activation_token = uuid.uuid4()  # Invalidate token
                profile.save()
                messages.success(request, 'Password reset successfully!')
                return redirect('login')
            else:
                messages.error(request, 'Passwords do not match or too short.')
        
        return render(request, 'registration/reset_password.html', {'token': token})
    except UserProfile.DoesNotExist:
        messages.error(request, 'Invalid reset link.')
        return redirect('forgot_password')

def send_password_reset_email(user, token):
    subject = 'Reset Your BoliBazaar Password'
    html_message = render_to_string('emails/password_reset.html', {
        'user': user,
        'token': token,
        'domain': 'localhost:8000'
    })
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=html_message,
        fail_silently=False,
    )

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    bids = product.bids.all()[:10]
    bid_form = BidForm()
    
    context = {
        'product': product,
        'bids': bids,
        'bid_form': bid_form,
        'top_bidders': product.top_bidders,
    }
    return render(request, 'auction/product_detail.html', context)

@login_required
@csrf_exempt
def place_bid(request, pk):
    if request.method == 'POST':
        # Check if user email is verified
        try:
            profile = UserProfile.objects.get(user=request.user)
            if not profile.is_email_verified:
                return JsonResponse({
                    'success': False, 
                    'error': 'Please verify your email before placing bids. Check your inbox.'
                })
        except UserProfile.DoesNotExist:
            return JsonResponse({
                'success': False, 
                'error': 'Please complete your profile verification.'
            })
        
        product = get_object_or_404(Product, pk=pk)
        
        if product.is_expired:
            return JsonResponse({'success': False, 'error': 'Auction has ended'})
        
        try:
            data = json.loads(request.body)
            amount = float(data.get('amount', 0))
        except:
            amount = float(request.POST.get('amount', 0))
        
        current_highest = product.current_highest_bid
        
        if amount <= current_highest:
            return JsonResponse({
                'success': False, 
                'error': f'Bid must be higher than current highest bid of ₹{current_highest}'
            })
        
        bid = Bid.objects.create(
            product=product,
            bidder=request.user,
            amount=amount
        )
        
        # Send bid confirmation email
        is_highest = (amount == product.current_highest_bid)
        send_bid_confirmation_email(
            request.user, 
            product, 
            amount, 
            is_highest, 
            product.current_highest_bid
        )
        
        return JsonResponse({
            'success': True,
            'new_highest_bid': amount,
            'bidder_name': request.user.get_full_name() or request.user.username,
            'message': f'Bid of ₹{amount} placed successfully!'
        })
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@csrf_exempt
def get_current_bid(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return JsonResponse({
        'current_bid': float(product.current_highest_bid),
        'product_name': product.title
    })

@login_required
def dashboard(request):
    user_bids = Bid.objects.filter(bidder=request.user).order_by('-timestamp')
    return render(request, 'auction/dashboard.html', {'user_bids': user_bids})

def is_admin(user):
    return user.is_staff or user.is_superuser

@user_passes_test(is_admin)
def admin_dashboard(request):
    products = Product.objects.all().order_by('-created_at')
    total_bids = Bid.objects.count()
    active_auctions = Product.objects.filter(is_active=True, end_time__gt=timezone.now()).count()
    
    context = {
        'products': products,
        'total_bids': total_bids,
        'active_auctions': active_auctions,
    }
    return render(request, 'auction/admin_dashboard.html', context)

@user_passes_test(is_admin)
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product added successfully!')
            return redirect('admin_dashboard')
    else:
        form = ProductForm()
    return render(request, 'auction/add_product.html', {'form': form})

@user_passes_test(is_admin)
def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully!')
            return redirect('admin_dashboard')
    else:
        form = ProductForm(instance=product)
    return render(request, 'auction/edit_product.html', {'form': form, 'product': product})

@user_passes_test(is_admin)
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully!')
        return redirect('admin_dashboard')
    return render(request, 'auction/delete_product.html', {'product': product})

@user_passes_test(is_admin)
def generate_report(request):
    format_type = request.GET.get('format', 'pdf')
    product_id = request.GET.get('product_id')
    
    if product_id:
        products = Product.objects.filter(id=product_id)
    else:
        products = Product.objects.all()
    
    if format_type == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="auction_report.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Product', 'Winner', 'Winning Bid', 'Total Bids', 'Status'])
        
        for product in products:
            winner = product.highest_bidder
            winner_name = winner.get_full_name() if winner else 'No bids'
            status = 'Closed' if product.is_expired else 'Active'
            
            writer.writerow([
                product.title,
                winner_name,
                product.current_highest_bid,
                product.bids.count(),
                status
            ])
        
        return response
    
    else:  # PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="auction_report.pdf"'
        
        p = canvas.Canvas(response, pagesize=letter)
        width, height = letter
        
        p.drawString(100, height - 100, "BoliBazaar Auction Report")
        y = height - 150
        
        for product in products:
            winner = product.highest_bidder
            winner_name = winner.get_full_name() if winner else 'No bids'
            status = 'Closed' if product.is_expired else 'Active'
            
            p.drawString(100, y, f"Product: {product.title}")
            p.drawString(100, y - 20, f"Winner: {winner_name}")
            p.drawString(100, y - 40, f"Winning Bid: ₹{product.current_highest_bid}")
            p.drawString(100, y - 60, f"Total Bids: {product.bids.count()}")
            p.drawString(100, y - 80, f"Status: {status}")
            y -= 120
            
            if y < 100:
                p.showPage()
                y = height - 100
        
        p.save()
        return response