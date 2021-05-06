from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import ProfileUpdateForm, UserUpdateForm, BecomeSeller
from django.contrib import messages
from .models import User, Profile
from core.models import Order, Item
# Create your views here.


@login_required
def profile(request):
    """This view provides form for users to update their profile."""
    if request.method == 'POST':
        p_form = ProfileUpdateForm(
            request.POST, 
            request.FILES, 
            instance=request.user.profile)
        u_form = UserUpdateForm(request.POST, instance=request.user)

        if p_form.is_valid() and u_form.is_valid():
            p_form.save()
            u_form.save()
            messages.success(
                request, 'Your profile has been updated!'
                )  
            return redirect('users:dashboard')
    else:
        p_form = ProfileUpdateForm(instance=request.user.profile)
        u_form = UserUpdateForm(instance=request.user)
    return render(request, 'users/profile.html', {
        'p_form':p_form, 
        'u_form':u_form
        })

@login_required
def dashboard(request):
    user = request.user
    if user.seller:
        if 'payout' in request.POST:
            pay = request.POST['payout']
            
            if float(pay) >= 100:
                messages.success(request, f'Your request for the payment of ${pay} was successful!\
                    Please update your bank account details in your profile.')
            else:
                messages.warning(request, f'Your request for the payment of ${pay} was unsuccessful.\
                    Your earning is less than the payout threshold of $100.')
        items = Item.objects.filter(user=user)
        context = {
            'items':items
        }
        return render(request, 'users/admin.html', context)
    else:
        orders = Order.objects.filter(user=user).order_by('-id')
        form = BecomeSeller()
        context = {
            'orders': orders,
            'form':form
        }
        return render(request, 'users/dashboard.html', context)

@login_required
def become_a_seller(request):
    if request.method == 'POST':
        form = BecomeSeller(request.POST)
        if form.is_valid():
            business_name = form.cleaned_data.get('business_name')
            experience = form.cleaned_data.get('experience')

            request.user.profile.business_name = business_name
            request.user.profile.experience = experience
            request.user.profile.save()
            request.user.seller = True
            request.user.customer = False
            request.user.save()
            messages.success(request, 'You have successflu signed up a seller.')
            return redirect('/dashboard')
    else:
        form = BecomeSeller()
    return render(request, 'form.html', {'form':form})

def earnings(request):
    user = request.user
    if user.seller:
        items = Item.objects.filter(user=user)
        total_earning = 0
        earning = 0
        for item in items:
            if item.discount_price:
                earning = item.downloads * item.discount_price
                total_earning += earning
            else:
                earning = item.downloads * item.price
                total_earning += earning
        context = {
            'items':items,
            'total_earning':total_earning
        }
        return render(request, 'users/earnings.html', context)
    else:
        return redirect('/dashboard')