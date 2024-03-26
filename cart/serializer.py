from rest_framework import serializers
from .models import Cart, CartItems
from book.models import Books

class ItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = CartItems
        fields = ('id', 'price', 'quantity', 'book', 'cart')

class CartSerializer(serializers.ModelSerializer):
    book = serializers.PrimaryKeyRelatedField(queryset=Books.objects.all(), write_only=True)
    quantity = serializers.IntegerField(write_only=True)
    cart_items = serializers.SerializerMethodField(read_only=True, method_name='cart_items_details')
    
    class Meta:
        model = Cart
        fields = ('id', 'total_price', 'total_quantity', 'is_ordered', 'ordered_at', 'user', 'book', 'quantity', 'cart_items')
        
    def cart_items_details(self, cart):
        items = cart.cartitems_set.all()
        items_list = ItemSerializer(items, many=True)        
        return items_list.data
        
    def create(self, validated_data):
        book = validated_data['book']
        cart = Cart.objects.filter(user_id=validated_data['user'].id, is_ordered=False).first()
        if book.quantity < validated_data['quantity']:
            raise serializers.ValidationError("Book is out of stock")
        if not cart:
            cart = Cart.objects.create(user=validated_data['user'])
            cart_item = CartItems.objects.create(cart_id=cart.id, book_id=book.id, price=book.price, quantity=validated_data['quantity'])
        else:
            cart_items = CartItems.objects.filter(book_id=book.id, cart_id=cart.id) 
            if cart_items.exists():
                cart_item = cart_items.first()
                cart_item.quantity = validated_data['quantity']
                cart_item.save()
            else:
                cart_item = CartItems.objects.create(quantity=validated_data['quantity'],
                                                     price=book.price,
                                                     book_id=book.id,
                                                     cart_id=cart.id)
        items = cart.cartitems_set.all()
        cart.total_quantity = sum([x.quantity for x in items])
        cart.total_price = sum([x.price * x.quantity for x in items])
        cart.save()        
        return cart
        