from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, View, CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.utils import timezone
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from .models import Item, OrderItem, Order, Payment, Category
from django.conf import settings
from .utils import id_generator
from django.conf import settings

from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import send_mail


#Paystack api
from paystackapi.transaction import Transaction
from paystackapi.customer import Customer
from paystackapi.subscription import Subscription as Sub
from paystackapi.paystack import Paystack
paystack = Paystack(secret_key=settings.PAYSTACK_SECRET_KEY)
from users.models import User


# Create your views here.

class HomeView(ListView):
    """This view lists the products on the homepage."""
    model = Item
    paginate_by = 4
    ordering = ['-id']
    template_name = 'core/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'categories': Category.objects.all().order_by('-id')[:5] 
        })
        if 'page' in self.request.GET:
            return context 
        return context


class ItemDetailView(DetailView):
    """This is the detail view for each product or item."""
    model = Item
    template_name = 'core/photo-detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'categories': Category.objects.all().order_by('-id')[:5] 
        })
        context['rel_items'] = [x for x in Item.objects.filter(
            category=context['object'].category)]
        context['user_rel_items'] = [x for x in Item.objects.filter(
            user=context['object'].user)]

        # remove the current item from the related items
        if context['object'] in context['rel_items']:
            context['rel_items'].remove(context['object'])

        # remove the current item from the related items
        if context['object'] in context['user_rel_items']:
            context['user_rel_items'].remove(context['object'])
        return context

class TagItemListView(ListView):
    """TagItemListView lists all the items under a particular tag.
    """
    model = Item
    # context_object_name = 'posts'
    ordering = ['-id']
    paginate_by = 12
    template_name = 'core/item_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'objects': Item.objects.all().order_by('-id')[:5],
            'categories': Category.objects.all().order_by('-id')[:5] 
        })
        if 'page' in self.request.GET:
            return context 
        return context  

    def get_queryset(self):
        tag = get_object_or_404(Category, name=self.kwargs.get('name'))
        return Item.objects.filter(category=tag).order_by('-id')

class AuthorItemListView(ListView):
    """AuthorItemListView lists all the posts by a particular user(author).
    """
    model = Item
    # context_object_name = 'posts'
    paginate_by = 12

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'objects': Item.objects.all().order_by('-id')[:5],
            'categories': Category.objects.all().order_by('-id')[:5]  
        })
        if 'page' in self.request.GET:
            return context 
        return context

    def get_queryset(self):
        user = get_object_or_404(User, id=self.kwargs.get('id'))
        self.kwargs.update({'first_name':user.first_name})
        return Item.objects.filter(user=user).order_by('-id')

class OrderSummaryView(LoginRequiredMixin, View):
    """This is the detail view for each product or item.order summary view -- Cart"""
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {'object':order}
            return render(self.request, 'core/order_summary.html', context)
        except ObjectDoesNotExist:
            messages.info(self.request, f'Your Cart is empty.')
            return redirect('/')


class PaymentView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):

        if 'price' in self.request.GET and 'slug' in self.request.GET:
            total = self.request.GET['price']
            slug = self.request.GET['slug']
        
            item = get_object_or_404(Item, slug=slug)
            order_item, created = OrderItem.objects.get_or_create(
                item=item,
                user=self.request.user,
                ordered=False
                )

            # order
            try:
                order_qs = Order.objects.filter(user=self.request.user, ordered=False)

                if order_qs.exists():
                    order = order_qs[0]
                    if order.items.filter(item__slug=item.slug).exists():
                        pass
                    # if the order_item is not there, add it to the order. 
                    else:
                        order_item.quantity = 1
                        order.items.add(order_item)
                        order.save()
                # if the order_qs does not exist, create a new order
                else:
                    ordered_date = timezone.now()
                    order = Order.objects.create(
                        user=self.request.user, 
                        ordered_date=ordered_date,
                        order_id=id_generator()
                        )
                    # set the qty of the order_item to the value 1
                    order_item.quantity = 1
                    order_item.save()
                    order.items.add(order_item)
                    total = order.get_total()
                    
            except ObjectDoesNotExist:
                messages.info(self.request, f'Your cart is empty.')
                return redirect('/')
        else:
            try:
                order = Order.objects.get(
                    user = self.request.user,
                    ordered = False
                )
                total = order.get_total()
            except ObjectDoesNotExist:
                messages.info(self.request, f'Your cart is empty.')
                return redirect('/')


        publicKey = settings.PAYSTACK_PUBLIC_KEY

        try:
            if self.request.method == 'GET':
                reference = self.request.GET['reference']
                verify_payment = Transaction.verify(reference=reference)
                print(verify_payment)
                # authorization = verify_payment['data']['authorization']['authorization_code']
                
                #verify transaction and make the order
                if verify_payment['status'] == True:
                    # create the payment
                    payment = Payment()
                    payment.paystack_transaction_id = reference
                    payment.user = self.request.user
                    payment.amount = order.get_total()
                    payment.save()

                    #assign payment to the order
                    order.ordered = True
                    order.payment = payment
                    order.save()

                    # reduce the qty of the item by qty purchased by this user.
                    for order_item in order.items.all():
                        # check if the item has a qty.
                        if order_item.item.quantity:
                            order_item.item.quantity -= order_item.quantity
                            order_item.item.downloads += order_item.quantity
                            # check if the item qty is more than 0
                            if order_item.item.quantity > 0:
                                order_item.item.save()
                            # if the qty is less, just make it 0. 
                            else:
                                order_item.item.quantity = 0
                                order_item.item.save()

                    # SEND ORDER MAIL TO THE CUSTOMER FOR SUCCESFUL ORDER
                    contexts = {
                        'email':order.user.email,
                        'name':order.user.first_name.capitalize,
                        'order_id':order.order_id,
                        'items':order.items.all(),
                        'date':order.ordered_date.date(),
                        'total':total,
                        'payment':order.payment.amount,
                        'timestamp':order.payment.timestamp
                    }
                    subject = 'ImgRepo: Your file is ready for download!'
                    body = render_to_string('emails/customer_order.html', contexts)
                    plain_body = strip_tags(body)

                    send_mail(
                        subject, 
                        plain_body, 
                        'rasholayemi@gmail.com', 
                        [order.user.email],
                        html_message=body
                        )

                    # SEND ORDER MAIL TO THE ADMIN FOR SUCCESFUL ORDER
                    var = {
                        'email':order.user.email,
                        'name':order.user.first_name.capitalize,
                        'order_id':order.order_id,
                        'items':order.items.all(),
                        'date':order.ordered_date.date(),
                        'total':total,
                        'payment':order.payment.amount,
                        'timestamp':order.payment.timestamp,
                        'payment_id':order.payment.paystack_transaction_id
                    }
                    topic = 'ImgRepo: New order has been placed successfully!'
                    message = render_to_string('emails/admin_order.html', var)
                    plain_message = strip_tags(message)

                    send_mail(
                        topic, 
                        plain_message, 
                        'rasholayemi@gmail.com', 
                        ['rasholayemi@gmail.com'],
                        html_message=message
                        )
                    #assign to session
                    self.request.session['order_id'] = order.id
                    messages.success(self.request, f'Your order has been successfully placed.')
                    print('SUCCESS!!!!!!!!!!!!!!!')
                    return redirect('core:thanks')
                else:
                    messages.error(self.request, f'Something went wrong. You were not charged. Please try again.')
        
        except:
            pass

        
        context = {
            'order':order,
            'total':total,
            'publicKey':publicKey,
            'email':self.request.user.email
        }
        return render(self.request, 'core/payment.html', context)

@login_required
def add_to_cart(request, slug):
    """
    Gets the item whose slug is passed in and creates an OrderItem
    using that item.
    """
    # get the quantity of the item from the POST request
    if request.method == 'POST':
        qty = request.POST['qty']

        item = get_object_or_404(Item, slug=slug)
        order_item, created = OrderItem.objects.get_or_create(
            item=item,
            user=request.user,
            ordered=False
            )

        # filter the order queryset using the logged in user and 
        # making sure the order hasn't been completed i.e ordered = False
        order_qs = Order.objects.filter(user=request.user, ordered=False)

        if order_qs.exists():
            order = order_qs[0]
            # check if the order_item is in the order
            if order.items.filter(item__slug=item.slug).exists():
                order_item.quantity += int(qty)
                order_item.save()

                messages.success(request, f'Product quantity updated in cart successfully.')
                return redirect('core:item-detail', slug=slug)
            
            # if the order_item is not there, add it to the order. 
            else:
                order_item.quantity = qty
                order_item.save()
                order.items.add(order_item)
                messages.success(request, f'Product added to cart successfully.')
                return redirect('core:item-detail', slug=slug)

        # if the order_qs does not exist, create a new order
        else:
            ordered_date = timezone.now()
            order = Order.objects.create(
                user=request.user, 
                ordered_date=ordered_date,
                order_id=id_generator()
                )
            # set the qty of the order_item to the value the user passed in
            # check if the item qty is enough to supply the qty by the customer.
            order_item.quantity = qty
            order_item.save()
            order.items.add(order_item)
            messages.success(request, f'Product added to cart successfully.')
            return redirect('core:item-detail', slug=slug)
        
    else:
        return redirect('core:item-detail', slug=slug)

@login_required
def remove_from_cart(request, slug):
    """
    Gets the item whose slug is passed in and removes the OrderItem
    from the order.
    """
    item = get_object_or_404(Item, slug=slug)

    # filter out the user order that hasn't been ordered or completed yet
    order_qs = Order.objects.filter(user=request.user, ordered=False)

    if order_qs.exists():
        order = order_qs[0]

        # check if the order_item is in the order then remove it
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
                )[0] 
            order.items.remove(order_item)
            messages.success(request, f"Product removed from cart.")
            return redirect('core:order-summary')
        # if the order_item is not there, send back an error message.
        else:
            messages.warning(request, f"Your cart doesn't contain this product.")
            return redirect('core:order-summary')
    else:
        messages.info(request, f'Your cart is empty')
        return redirect('core:order-summary')
    
@login_required
# reduces the quantity of an existing order_item in the cart
def remove_single_item_from_cart(request, slug):
    """
    reduces the quantity of an existing order_item in the cart
    """
    item = get_object_or_404(Item, slug=slug)

    # filter out the user order that hasn't been ordered or completed yet
    order_qs = Order.objects.filter(user=request.user, ordered=False)

    if order_qs.exists():
        order = order_qs[0]

        # check if the order_item is in the order then remove it
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
                )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, f"Product quantity was updated.")
            return redirect('core:order-summary')

@login_required
# increases the quantity of an already existing order_item in the cart.
def increment_order_item_qty(request, slug):
    """
        Increases the quantity of an already existing order_item
        in the Cart. 
    """
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
        )

    # filter the order queryset using the logged in user and 
    # making sure the order hasn't been completed i.e ordered = False
    order_qs = Order.objects.filter(user=request.user, ordered=False)

    if order_qs.exists():
        order = order_qs[0]
        # check if the order_item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            # check if the item qty is enough to supply the qty requested by the customer.
            if item.quantity >= order_item.quantity:
                order_item.save()
            messages.success(request, f'Product quantity updated in cart successfully.')
            return redirect('core:order-summary')


def search(request):
    query = request.GET['query']
    
    items = Item.objects.filter(name__icontains=query) | Item.objects.filter(description__icontains=query)
    category = Category.objects.filter(name__icontains=query)
	

    context = {
        'object_list':items,
        'query':query,
        'category':category,
        'categories': Category.objects.all().order_by('-id')[:4], 
        'year':timezone.now().year,
    }
    
    # To display the items in the cart:
    try:
        order = Order.objects.get(user=request.user, ordered=False)
        context['order'] = order
    except:
        context['order'] = None
    return render(request, 'core/search.html', context)

@login_required
def thanks(request):
    try:
        order_id = request.session['order_id']
        order = Order.objects.filter(id=order_id)[0]

        context = {
            'order_items':order.items.all().first()
        }
        return render(request, 'core/thank-you.html', context)
    except:
        return redirect('/')


"""

CREATE, DELETE, UPDATE ITEMS, 

"""

class ItemCreateView(LoginRequiredMixin, CreateView):
    """ItemCreateView creates a new Item.
    NOTE: user has to be authenticated to create a Item.
    """
    model = Item
    fields = [
        'name', 'image', 'category', 'price', 
        'discount_price', 'description', 'downloadable_file','dimension', 'format'
        ]
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.add_message(self.request, messages.SUCCESS, 'Image uploaded successfully.')
        return super().form_valid(form)
    
    def test_func(self):
        if self.request.user.seller:
            return True
        return False
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'tags': Category.objects.all().order_by('-id')
        })  
        return context

class ItemUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """ ItemUpdateView updates an existing Item.
        NOTE: 
            1. user must be authenticated to update an Item. 
            2. user must be the owner of an item to update that item.
    """
    model = Item
    fields = [
        'name', 'image', 'category', 'price', 
        'discount_price', 'description', 'downloadable_file', 'dimension', 'format'
        ]

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.add_message(self.request, messages.SUCCESS, 'Image updated successfully.')
        return super().form_valid(form)

    def test_func(self):
        item = self.get_object()
        if self.request.user == item.user:
            return True
        return False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'user': self.request.user.item_set.get(slug=self.kwargs.get('slug')),
            'tags': Category.objects.all().order_by('-id')
        })  
        return context

class ItemDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """PostDeleteView deletes an existing post. 
        NOTE: 
            1. user must be authenticated to delete an item. 
            2. user must be owner of an item to delete that item.
    """
    model = Item
    success_url = '/dashboard'

    def test_func(self):
        item = self.get_object()
        if self.request.user == item.user:
            return True
        return False