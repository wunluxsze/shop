from django.contrib.auth import logout
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView, ListAPIView, ListCreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.status import HTTP_200_OK
from .models import User, Products, Country, Cart, Order, Manufacturer
from .serializers import UserRegisterSerializer, UserLoginSerializer, ProductSerializer, ManufacturerSerializer, CartSerializer, OrderSerializer
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes


@api_view(['GET', "POST"])
@permission_classes((AllowAny,))
def get_create_products(request):
    if request.method == "GET":
        products = Products.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = ProductSerializer(data=request.data)
        if request.user.is_superuser:
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


@api_view(['PATCH', "GET", 'DELETE'])
@permission_classes((AllowAny,))
def get_edit_delete_product(request, pk):
    if request.method == 'GET':
            try:
                products = Products.objects.get(id=pk)
            except:
                return Response(status=status.HTTP_404_NOT_FOUND)
            serializer = ProductSerializer(products, many=False)
            return Response(serializer.data)
    elif request.method == "PATCH":
        if request.user.is_superuser:
            try:
                product = Products.objects.get(id=pk)
            except:
                return Response(status=status.HTTP_404_NOT_FOUND)
            serializer = ProductSerializer(data=request.data, instance=product, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)
    elif request.method == 'DELETE':
        if request.user.is_superuser:
            try:
                product = Products.objects.get(id=pk)
                product.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except Products.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


@api_view(['GET'])
def create_order(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)

    order = Order.objects.create(user=request.user)
    total = 0
    for product in cart.products.all():
        total += product.price
        order.products.add(product)

    order.totalPrice = total
    order.save()

    cart.products.clear()

    serializer = OrderSerializer(order)

    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def add_to_cart(request, product_id):
    try:
        product = Products.objects.get(pk=product_id)
    except Products.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    cart, _ = Cart.objects.get_or_create(user=request.user)

    cart.products.add(product)

    serializer = CartSerializer(cart)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((AllowAny,))
def get_manufacturer(request, pk):
    try:
        manufacturer = Manufacturer.objects.get(id=pk)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)
    serializer = ManufacturerSerializer(manufacturer, many=False)
    return Response(serializer.data)


@api_view(['GET', "POST"])
@permission_classes((AllowAny,))
def get_create_manufacturer(request):
    if request.method == "GET":
        manufacturer = Manufacturer.objects.all()
        serializer = ManufacturerSerializer(manufacturer, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = ManufacturerSerializer(data=request.data)
        if request.user.is_superuser:
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


@api_view(['PATCH'])
@permission_classes((IsAdminUser,))
def edit_maufacturer(request, pk):
    try:
        manufacturer = Manufacturer.objects.get(id=pk)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)
    serializer = ManufacturerSerializer(data=request.data, instance=manufacturer, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes((IsAdminUser,))
def delete_manufacturer(request, pk):
    try:
        manufacturer = Manufacturer.objects.get(id=pk)
        manufacturer.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)

class RegisterUserView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny, ]

    def post(self, request, *args, **kwargs):
        serializer = UserRegisterSerializer(data=request.data)
        data = {}
        if serializer.is_valid():
            serializer.save()
            data['data'] = serializer.data
            user = serializer.user
            token = Token.objects.create(user=user)
            print(Token)
            return Response({'user_token': token.key}, status=status.HTTP_200_OK)
        else:
            data = serializer.errors
            return Response(data)

class LoginUserView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserLoginSerializer
    permission_classes = [AllowAny, ]

    def post(self, request, *args, **kwargs):
        serializer = UserLoginSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({
                'error': {
                    'code': 401,
                    'message': 'Authenticated Failed'
                }
            })
        user = serializer.validated_data
        print('kostya', user)
        if user:
            token_object, token_created = Token.objects.get_or_create(user=user)
            token = token_object if token_object else token_created

            return Response({'user_token': token.key}, status=HTTP_200_OK)
        return Response({'error': {'message': 'Authenticated failed'}})

class LogOutUserView(ListAPIView):
    def get(self, request, *args, **kwargs):
        try:
            request.user.auth_token.delete()
        except (AttributeError, ObjectDoesNotExist):
            return Response({
                {'error': {
                    'code': 401,
                    'message': 'Logout failed'
                }
                }
            }, status=401)

        logout(request)

        return Response({
            'data': {
                'message': 'logout'
            }
        }, status=200)