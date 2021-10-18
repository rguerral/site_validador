from django.urls import path, reverse_lazy
from . import views

app_name='catalog'
urlpatterns = [

    path('bids',
        views.BidList.as_view(),
        name='bids'),

    path('bid/create', 
        views.BidCreate.as_view(),
         name='bid_create'),
    
    path('bid/<int:pk>/update', 
        views.BidUpdate.as_view(),
         name='bid_update'),
    
    path('bid/<int:pk>/delete', 
        views.BidDelete.as_view(),
         name='bid_delete'),

    path('bid/<int:pk>',
        views.BidDetail.as_view(),
        name='bid_detail'),

    path('bid/<int:pk>/attributes',
        views.BidAttributeList.as_view(),
        name='bidattribute_list'),

    path('bid/<int:pk>/create_bidattribute',
        views.BidAttributeCreate.as_view(),
        name='bidattribute_create'),

    path('bidattribute/<int:pk>/update',
        views.BidAttributeUpdate.as_view(),
        name='bidattribute_update'),

    path('bidattribute/<int:pk>/delete',
        views.BidAttributeDelete.as_view(),
        name='bidattribute_delete'),

    path('bidattribute/<int:pk>',
        views.BidAttributeDetail.as_view(),
        name='bidattribute_detail'),

    path('bidattribute/<int:pk>/create_level',
        views.BidAttributeLevelCreate.as_view(),
        name='bidattributelevel_create'),

    path('bidattributelevel/delete/<int:pk>',
        views.BidAttributeLevelDelete.as_view(),
        name='bidattributelevel_delete'),

    path('bid/<int:pk>/categories',
        views.CategoryList.as_view(),
        name='category_list'),

    path('category/<int:pk>',
        views.CategoryDetail.as_view(),
        name='category_detail'),
    
    path('bid/<int:pk>/create_category', 
        views.CategoryCreate.as_view(success_url=reverse_lazy('catalog:categories')),
         name='category_create'),
    
    path('category/<int:pk>/update', 
        views.CategoryUpdate.as_view(success_url=reverse_lazy('catalog:categories')),
         name='category_update'),
    
    path('category/<int:pk>/delete', 
        views.CategoryDelete.as_view(),
         name='category_delete'),
    
    path('category/<int:pk>/create_attribute', 
        views.AttributeCreate.as_view(),
         name='attribute_create'),

    path('attribute/<int:pk>/update', 
        views.AttributeUpdate.as_view(),
         name='attribute_update'),
    
    path('attribute/<int:pk>/delete', 
        views.AttributeDelete.as_view(),
         name='attribute_delete'),

    path('category/<int:pk>/create_product', 
        views.ProductCreate.as_view(),
         name='product_create'),

    path('product/<int:pk>/delete', 
        views.ProductDelete.as_view(),
         name='product_delete'),

    path('bid/<int:pk>/algorithms', 
        views.Algorithms.as_view(),
        name='algorithms'),

    path('bid/<int:pk>/simulate', 
        views.Simulate.as_view(),
        name='simulate'),

    path('bid/<int:pk>/json', 
        views.BuildJson,
        name='build_json'),

    path('bid/<int:pk>/template', 
        views.BuildTemplate,
        name='bid_template'),

    path('bid/<int:pk>/validate', 
    views.Validate.as_view(),
    name='validate'),

]
