from django.contrib import admin
from django_json_widget.widgets import JSONEditorWidget
from django.db import models
from django.utils.translation import gettext_lazy as _
from dal import autocomplete
from django.utils.html import format_html


from artd_product.models import (
    Tax,
    RootCategory,
    Category,
    Brand,
    Product,
    Image,
    ProductImage,
    GroupedProduct,
    CategoryByUrl,
)


class CategoryInline(admin.StackedInline):
    model = Category
    extra = 0
    show_change_link = True


class ProductImageInline(admin.StackedInline):
    model = ProductImage
    extra = 0
    show_change_link = True
    fields = (
        "image",
        "url_key",
        "status",
    )


@admin.register(Tax)
class TaxAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "id",
        "percentage",
        "status",
    )
    list_filter = (
        "name",
        "percentage",
        "status",
    )
    search_fields = (
        "name",
        "id",
        "percentage",
        "status",
    )
    readonly_fields = [
        "created_at",
        "updated_at",
    ]
    fieldsets = (
        (
            _("Tax Information"),
            {
                "fields": (
                    "name",
                    "percentage",
                )
            },
        ),
        (
            _("Status Information"),
            {
                "fields": ("status",),
            },
        ),
        (
            _("Source Information"),
            {
                "fields": (
                    "external_id",
                    "source",
                ),
            },
        ),
        (
            _("Timestamps"),
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )
    formfield_overrides = {
        models.JSONField: {"widget": JSONEditorWidget},
    }

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "id",
        "status",
    )
    list_filter = ("status",)
    search_fields = (
        "id",
        "name",
        "status",
    )
    readonly_fields = [
        "created_at",
        "updated_at",
    ]
    fieldsets = (
        (
            _("Brand Information"),
            {"fields": ("name","partner",)},
        ),
        (
            _("Status Information"),
            {
                "fields": ("status",),
            },
        ),
        (
            _("Source Information"),
            {
                "fields": (
                    "external_id",
                    "source",
                ),
            },
        ),
        (
            _("Timestamps"),
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )
    formfield_overrides = {
        models.JSONField: {"widget": JSONEditorWidget},
    }


@admin.register(RootCategory)
class RootCategoryAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "id",
        "partner",
        "status",
    )
    list_filter = ("status",)
    search_fields = (
        "id",
        "name",
        "status",
        "partner__name",
        "url_key",
        "meta_title",
        "meta_description",
        "meta_keywords",
    )
    readonly_fields = [
        "created_at",
        "updated_at",
    ]
    fieldsets = (
        (
            _("Root Category Information"),
            {
                "fields": (
                    "name",
                    "partner",
                    "short_description",
                    "description",
                )
            },
        ),
        (
            _("Image Information"),
            {
                "fields": (
                    "banner_image",
                    "mini_image",
                    "secondary_mini_image",
                ),
            },
        ),
        (
            _("Status Information"),
            {
                "fields": ("status",),
            },
        ),
        (
            _("SEO Information"),
            {
                "fields": (
                    "url_key",
                    "meta_title",
                    "meta_description",
                    "meta_keywords",
                ),
            },
        ),
        (
            _("Other Information"),
            {
                "fields": ("json_data",),
            },
        ),
        (
            _("Source Information"),
            {
                "fields": (
                    "external_id",
                    "source",
                ),
            },
        ),
        (
            _("Timestamps"),
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )

    formfield_overrides = {
        models.JSONField: {"widget": JSONEditorWidget},
    }


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "id",
        "partner",
        "root_category",
        "parent",
        "status",
    )
    list_filter = ("status",)
    search_fields = (
        "id",
        "name",
        "parent__name",
        "root_category__name",
        "status",
        "url_key",
        "meta_title",
        "meta_description",
        "meta_keywords",
    )
    readonly_fields = [
        "created_at",
        "updated_at",
    ]
    fieldsets = (
        (
            _("Category Information"),
            {
                "fields": (
                    "name",
                    "partner",
                    "root_category",
                    "parent",
                    "short_description",
                    "description",
                )
            },
        ),
        (
            _("Image Information"),
            {
                "fields": (
                    "banner_image",
                    "mini_image",
                    "secondary_mini_image",
                ),
            },
        ),
        (
            _("Status Information"),
            {
                "fields": ("status",),
            },
        ),
        (
            _("SEO Information"),
            {
                "fields": (
                    "url_key",
                    "meta_title",
                    "meta_description",
                    "meta_keywords",
                ),
            },
        ),
        (
            _("Other Information"),
            {
                "fields": ("json_data",),
            },
        ),
        (
            _("Source Information"),
            {
                "fields": (
                    "external_id",
                    "source",
                ),
            },
        ),
        (
            _("Timestamps"),
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )
    formfield_overrides = {
        models.JSONField: {"widget": JSONEditorWidget},
    }


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "grouped_product_name",
        "sku",
        "grouped_product_sku",
        "brand",
        "status",
    )
    list_filter = (
        "name",
        "brand",
        "status",
    )
    search_fields = (
        "id",
        "name",
        "brand__name",
        "status",
        "sku",
        "url_key",
        "meta_title",
        "meta_description",
        "meta_keywords",
        "groupedproduct__name",
        "groupedproduct__sku",
    )
    readonly_fields = [
        "created_at",
        "updated_at",
    ]

    fieldsets = (
        (
            _("Product Information"),
            {
                "fields": (
                    "partner",
                    "url_key",
                    "name",
                    "type",
                    "brand",
                    "sku",
                    "short_description",
                    "description",
                    "tax",
                )
            },
        ),
        (
            _("Measurement Information"),
            {
                "fields": (
                    "weight",
                    "unit_of_measure",
                    "measure",
                ),
            },
        ),
        (
            _("Status Information"),
            {
                "fields": ("status",),
            },
        ),
        (
            _("Category Information"),
            {
                "fields": ("categories",),
            },
        ),
        (
            _("SEO Information"),
            {
                "fields": (
                    "meta_title",
                    "meta_description",
                    "meta_keywords",
                ),
            },
        ),
        (
            _("Other Information"),
            {
                "fields": ("json_data",),
            },
        ),
        (
            _("Source Information"),
            {
                "fields": (
                    "external_id",
                    "source",
                ),
            },
        ),
        (
            _("Timestamps"),
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )
    inlines = [ProductImageInline]
    formfield_overrides = {
        models.JSONField: {"widget": JSONEditorWidget},
        models.ManyToManyField: {"widget": autocomplete.ModelSelect2Multiple()},
    }


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = (
        "external_id",
        "image_preview",
        "id",
        "alt",
        "status",
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" height="50" />', obj.image.url)
        else:
            return "N/A"

    search_fields = (
        "external_id",
        "alt",
        "id",
    )
    formfield_overrides = {
        models.JSONField: {"widget": JSONEditorWidget},
    }
    readonly_fields = [
        "created_at",
        "updated_at",
    ]
    fieldsets = (
        (
            _("Image Information"),
            {
                "fields": (
                    "partner",
                    "image",
                    "alt",
                    "status",
                )
            },
        ),
        (
            _("Source Information"),
            {
                "fields": (
                    "external_id",
                    "source",
                ),
            },
        ),
        (
            _("Timestamps"),
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "id",
        "image",
        "status",
    )
    list_filter = ("status",)
    search_fields = (
        "product__name",
        "image__alt",
        "status",
        "id",
    )
    readonly_fields = [
        "created_at",
        "updated_at",
    ]
    fieldsets = (
        (
            _("Product Image Information"),
            {
                "fields": (
                    "product",
                    "image",
                    "url_key",
                )
            },
        ),
        (
            _("Status Information"),
            {
                "fields": ("status",),
            },
        ),
        (
            _("Source Information"),
            {
                "fields": (
                    "external_id",
                    "source",
                ),
            },
        ),
        (
            _("Timestamps"),
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )
    formfield_overrides = {
        models.JSONField: {"widget": JSONEditorWidget},
    }


@admin.register(GroupedProduct)
class GroupedProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "id",
        "sku",
        "status",
    )
    list_filter = ("status",)
    search_fields = (
        "id",
        "name",
        "sku",
        "status",
    )
    readonly_fields = [
        "created_at",
        "updated_at",
    ]
    fieldsets = (
        (
            _("Grouped Product Information"),
            {
                "fields": (
                    "partner",
                    "url_key",
                    "name",
                    "sku",
                    "short_description",
                    "description",
                )
            },
        ),
        (
            _("Products"),
            {
                "fields": ("products",),
            },
        ),
        (
            _("Status Information"),
            {
                "fields": ("status",),
            },
        ),
        (
            _("SEO Information"),
            {
                "fields": (
                    "meta_title",
                    "meta_description",
                    "meta_keywords",
                ),
            },
        ),
        (
            _("Source Information"),
            {
                "fields": (
                    "external_id",
                    "source",
                ),
            },
        ),
        (
            _("Timestamps"),
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )
    formfield_overrides = {
        models.JSONField: {"widget": JSONEditorWidget},
        models.ManyToManyField: {"widget": autocomplete.ModelSelect2Multiple()},
    }


@admin.register(CategoryByUrl)
class CategoryByUrlAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "url",
        "id",
    )
    list_filter = ("status",)
    search_fields = (
        "name",
        "url",
        "id",
    )
    readonly_fields = [
        "created_at",
        "updated_at",
    ]
    fieldsets = (
        (
            _("Category By Url Information"),
            {
                "fields": (
                    "name",
                    "url",
                )
            },
        ),
        (
            _("Categories"),
            {
                "fields": ("categories",),
            },
        ),
        (
            _("Status Information"),
            {
                "fields": ("status",),
            },
        ),
        (
            _("Source Information"),
            {
                "fields": (
                    "external_id",
                    "source",
                ),
            },
        ),
        (
            _("Timestamps"),
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )
    formfield_overrides = {
        models.JSONField: {"widget": JSONEditorWidget},
        models.ManyToManyField: {"widget": autocomplete.ModelSelect2Multiple()},
    }
