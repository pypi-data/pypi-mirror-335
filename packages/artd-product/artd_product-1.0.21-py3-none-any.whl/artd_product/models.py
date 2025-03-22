"""
 * Copyright (C) ArtD SAS - All Rights Reserved
 * Unauthorized copying of this file, via any medium is strictly prohibited
 * Proprietary and confidential
 * Written by Jonathan Favian Urzola Maldonado <jonathan@artd.com.co>, 2023
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from artd_partner.models import Partner
from artd_urls.models import Url


class ProductBaseModel(models.Model):
    created_at = models.DateTimeField(
        _("Created at"),
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        _("Updated at"),
        auto_now=True,
    )
    status = models.BooleanField(
        _("status"),
        default=True,
    )
    source = models.JSONField(
        _("Source"),
        help_text=_("Enter the source of the product"),
        null=True,
        blank=True,
        default=dict,
    )
    json_data = models.JSONField(
        _("Json data"),
        help_text=_("Enter the json data of the product"),
        null=True,
        blank=True,
        default=dict,
    )
    external_id = models.CharField(
        _("External id"),
        help_text=_("Enter the external id of the product"),
        max_length=250,
        null=True,
        blank=True,
    )

    class Meta:
        abstract = True


UNITS_OF_MEASURE = [
    ("kg", _("Kilogram")),
    ("g", _("Gram")),
    ("l", _("Liter")),
    ("ml", _("Milliliter")),
    ("m", _("Meter")),
    ("cm", _("Centimeter")),
    ("mm", _("Millimeter")),
    ("in", _("Inch")),
    ("ft", _("Foot")),
    ("yd", _("Yard")),
    ("mi", _("Mile")),
    ("oz", _("Ounce")),
    ("lb", _("Pound")),
    ("st", _("Stone")),
    ("t", _("Ton")),
    ("gal", _("Gallon")),
    ("pt", _("Pint")),
    ("qt", _("Quart")),
    ("cup", _("Cup")),
    ("pc", _("Piece")),
    ("set", _("Set")),
    ("pair", _("Pair")),
    ("doz", _("Dozen")),
    ("box", _("Box")),
    ("pack", _("Pack")),
    ("roll", _("Roll")),
    ("bag", _("Bag")),
    ("bottle", _("Bottle")),
    ("tube", _("Tube")),
    ("can", _("Can")),
    ("jar", _("Jar")),
    ("case", _("Case")),
    ("other", _("Other")),
]
PRODUCT_TYPE = [
    ("service", _("Service")),
    ("physical", _("Physical")),
    ("virtual", _("Virtual")),
]


class SearchEngine(models.Model):
    url_key = models.SlugField(
        _("Url key"),
        help_text=_("Enter the url key of the search engine"),
        max_length=250,
    )
    meta_title = models.CharField(
        _("Meta title"),
        help_text=_("Enter the meta title of the search engine"),
        max_length=250,
    )
    meta_description = models.CharField(
        _("Meta description"),
        help_text=_("Enter the meta description of the search engine"),
        max_length=250,
    )
    meta_keywords = models.CharField(
        _("Meta keywords"),
        help_text=_("Enter the meta keywords of the search engine"),
        max_length=250,
    )

    class Meta:
        abstract = True


class Tax(ProductBaseModel):
    """Model definition for Tax."""
    name = models.CharField(
        _("Name"),
        help_text=_("Enter the name of the tax"),
        max_length=250,
    )
    percentage = models.DecimalField(
        _("Percentage"),
        help_text=_("Enter the percentage of the tax"),
        max_digits=5,
        decimal_places=2,
    )

    class Meta:
        """Meta definition for Tax."""

        verbose_name = _("Tax")
        verbose_name_plural = _("Taxes")

    def __str__(self):
        """Unicode representation of Tax."""
        return self.name


class Brand(ProductBaseModel, SearchEngine):
    """Model definition for Brand."""
    partner = models.ForeignKey(
        Partner,
        verbose_name=_("Partner"),
        help_text=_("Select the partner"),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    
    name = models.CharField(
        _("Name"),
        help_text=_("Enter the name of the brand"),
        max_length=250,
    )

    class Meta:
        """Meta definition for Brand."""

        verbose_name = _("Brand")
        verbose_name_plural = _("Brands")

    def __str__(self):
        """Unicode representation of Brand."""
        return self.name


class RootCategory(ProductBaseModel, SearchEngine):
    """Model definition for RootCategory."""

    name = models.CharField(
        _("Name"),
        help_text=_("Enter the name of the root category"),
        max_length=250,
    )
    json_data = models.JSONField(
        _("Json data"),
        help_text=_("Enter the json data of the root category"),
        null=True,
        blank=True,
        default=dict,
    )
    partner = models.ForeignKey(
        Partner,
        verbose_name=_("Partner"),
        help_text=_("Select the partner"),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    mini_image = models.ImageField(
        _("Mini mage"),
        help_text=_("Select the mini mage"),
        upload_to="category/images/",
        null=True,
        blank=True,
    )
    secondary_mini_image = models.ImageField(
        _("Secondary ini mage"),
        help_text=_("Select the secondary mini mage"),
        upload_to="category/images/",
        null=True,
        blank=True,
    )
    banner_image = models.ImageField(
        _("banner image"),
        help_text=_("Select the banner image"),
        upload_to="category/images/",
        null=True,
        blank=True,
    )
    short_description = models.TextField(
        _("Short description"),
        help_text=_("Enter the short description of the category"),
        null=True,
        blank=True,
    )
    description = models.TextField(
        _("Description"),
        help_text=_("Enter the description of the category"),
        null=True,
        blank=True,
    )

    class Meta:
        """Meta definition for RootCategory."""

        verbose_name = _("Root Category")
        verbose_name_plural = _("Root Categories")

    def __str__(self):
        """Unicode representation of RootCategory."""
        return self.name


class Category(ProductBaseModel, SearchEngine):
    """Model definition for Category."""

    name = models.CharField(
        _("Name"),
        help_text=_("Enter the name of the category"),
        max_length=250,
    )
    root_category = models.ForeignKey(
        RootCategory,
        verbose_name=_("Root category"),
        help_text=_("Select the root category"),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    partner = models.ForeignKey(
        Partner,
        verbose_name=_("Partner"),
        help_text=_("Select the partner"),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    parent = models.ForeignKey(
        "self",
        verbose_name=_("Parent category"),
        help_text=_("Select the Parent category"),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    mini_image = models.ImageField(
        _("Mini mage"),
        help_text=_("Select the mini mage"),
        upload_to="category/images/",
        null=True,
        blank=True,
    )
    secondary_mini_image = models.ImageField(
        _("Secondary mini image"),
        help_text=_("Secondary mini image"),
        upload_to="category/images/",
        null=True,
        blank=True,
    )
    banner_image = models.ImageField(
        _("banner image"),
        help_text=_("Select the banner image"),
        upload_to="category/images/",
        null=True,
        blank=True,
    )
    short_description = models.TextField(
        _("Short description"),
        help_text=_("Enter the short description of the category"),
        null=True,
        blank=True,
    )
    description = models.TextField(
        _("Description"),
        help_text=_("Enter the description of the category"),
        null=True,
        blank=True,
    )

    class Meta:
        """Meta definition for Category."""

        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

    def __str__(self):
        """Unicode representation of Category."""

        if self.parent:
            if self.parent.name:
                parent_name = self.parent.name
            else:
                parent_name = ""
            parent = " (" + _("Parent category: ") + parent_name + ") "
        else:
            parent = ""
        if self.root_category:
            if self.root_category.name:
                root_category = self.root_category.name
            else:
                root_category = ""
            root_category = " (" + _("Root category: ") + root_category + ") "
        else:
            root_category = ""
        return f"{self.name}{parent}{root_category}"

    # Create a function to get the children of a category in a tree structure
    def get_children(self):
        return self.get_children_count() > 0


class Image(models.Model):
    """Model definition for Image."""

    image = models.ImageField(
        _("Image"),
        help_text=_("Select the image"),
        upload_to="product/images/",
    )
    alt = models.CharField(
        _("Alt"),
        help_text=_("Enter the alt of the image"),
        max_length=250,
    )
    external_id = models.CharField(
        _("External id"),
        help_text=_("Enter the external id of the image"),
        max_length=250,
        null=True,
        blank=True,
    )
    partner = models.ForeignKey(
        Partner,
        verbose_name=_("Partner"),
        help_text=_("Select the partner"),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    source = models.JSONField(
        _("Source"),
        help_text=_("Enter the source of the image"),
        null=True,
        blank=True,
        default=dict,
    )
    created_at = models.DateTimeField(
        _("Created at"),
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        _("Updated at"),
        auto_now=True,
    )
    status = models.BooleanField(
        _("status"),
        default=True,
    )

    class Meta:
        """Meta definition for Image."""

        verbose_name = _("Image")
        verbose_name_plural = _("Images")

    def __str__(self):
        """Unicode representation of Image."""
        return f"ALT: {self.alt}"

    @property
    def imagen_url(self):
        if self.image:
            return self.image.url
        return ""


class Product(ProductBaseModel, SearchEngine):
    """Model definition for Product."""

    partner = models.ForeignKey(
        Partner,
        verbose_name=_("Partner"),
        help_text=_("Select the partner"),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    url_key = models.SlugField(
        _("Url key"),
        help_text=_("Enter the url key of the product"),
        max_length=250,
        null=True,
        blank=True,
    )
    type = models.CharField(
        _("Type"),
        help_text=_("Select the type of the product"),
        max_length=250,
        choices=PRODUCT_TYPE,
        default="physical",
    )
    name = models.CharField(
        _("Name"),
        help_text=_("Enter the name of the product"),
        max_length=250,
    )
    sku = models.SlugField(
        _("Sku"),
        help_text=_("Enter the sku of the product"),
        max_length=250,
    )
    description = models.TextField(
        _("Description"),
        help_text=_("Enter the description of the product"),
    )
    short_description = models.TextField(
        _("Short description"),
        help_text=_("Enter the short description of the product"),
    )
    brand = models.ForeignKey(
        Brand,
        verbose_name=_("brand"),
        help_text=_("Select the brand"),
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    categories = models.ManyToManyField(
        Category,
        verbose_name=_("Category"),
        help_text=_("Select the category"),
    )
    tax = models.ForeignKey(
        Tax,
        verbose_name=_("Tax"),
        help_text=_("Select the tax"),
        on_delete=models.CASCADE,
    )
    weight = models.DecimalField(
        _("Weight"),
        help_text=_("Enter the weight of the product"),
        max_digits=10,
        decimal_places=2,
        default=0.00,
    )
    unit_of_measure = models.CharField(
        _("Unit of measure"),
        help_text=_("Select the unit of measure of the product"),
        max_length=250,
        choices=UNITS_OF_MEASURE,
        default="kg",
    )
    measure = models.DecimalField(
        _("Measure"),
        help_text=_("Enter the measure of the product"),
        max_digits=10,
        decimal_places=2,
        default=0.00,
    )
    variations = models.JSONField(
        _("Variations"),
        help_text=_("Enter the variations of the grouped product"),
        null=True,
        blank=True,
        default=dict,
    )

    @property
    def grouped_product_name(self):
        grouped_product: GroupedProduct = self.groupedproduct_set.last()
        if grouped_product is not None:
            return grouped_product.name
        else:
            return ''

    @property
    def grouped_product_sku(self):
        grouped_product: GroupedProduct = self.groupedproduct_set.last()
        if grouped_product is not None:
            return grouped_product.sku
        else:
            return ''

    @property
    def grouped_product_id(self):
        grouped_product: GroupedProduct = self.groupedproduct_set.last()
        if grouped_product is not None:
            return grouped_product.id
        else: 
            return ''

    class Meta:
        """Meta definition for Product."""

        verbose_name = _("Product")
        verbose_name_plural = _("Products")

    def __str__(self):
        """Unicode representation of ProductImage."""
        grouped_product: GroupedProduct = self.groupedproduct_set.last()
        if grouped_product:
            return f"({grouped_product.name}) {self.name}"
        else:
            return self.name


class ProductImage(ProductBaseModel):
    """Model definition for ProductImage."""

    url_key = models.SlugField(
        _("Url key"),
        help_text=_("Enter the url key of the product"),
        max_length=250,
        null=True,
        blank=True,
    )
    product = models.ForeignKey(
        Product,
        verbose_name=_("Product"),
        help_text=_("Select the product"),
        on_delete=models.CASCADE,
    )
    image = models.ForeignKey(
        Image,
        verbose_name=_("Image"),
        help_text=_("Select the image"),
        on_delete=models.CASCADE,
    )

    class Meta:
        """Meta definition for ProductImage."""

        verbose_name = _("Product Image")
        verbose_name_plural = _("Product Images")

    def __str__(self):
        """Unicode representation of ProductImage."""
        grouped_product: GroupedProduct = self.product.groupedproduct_set.last()
        if grouped_product:
            return f"({grouped_product.name}) {self.product.name}"
        else:
            return self.product.name


class GroupedProduct(ProductBaseModel, SearchEngine):
    """Model definition for GroupedProduct."""

    partner = models.ForeignKey(
        Partner,
        verbose_name=_("Partner"),
        help_text=_("Select the partner"),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    url_key = models.SlugField(
        _("Url key"),
        help_text=_("Enter the url key of the product"),
        max_length=250,
        null=True,
        blank=True,
    )
    name = models.CharField(
        _("Name"),
        help_text=_("Enter the name of the grouped product"),
        max_length=250,
    )
    sku = models.SlugField(
        _("Sku"),
        help_text=_("Enter the sku of the grouped product"),
        max_length=250,
    )
    description = models.TextField(
        _("Description"),
        help_text=_("Enter the description of the grouped product"),
    )
    short_description = models.TextField(
        _("Short_description"),
        help_text=_("Enter the short description of the grouped product"),
    )
    products = models.ManyToManyField(
        Product,
        verbose_name=_("Product"),
        help_text=_("Select the product"),
    )
    variations = models.JSONField(
        _("Variations"),
        help_text=_("Enter the variations of the grouped product"),
        null=True,
        blank=True,
        default=dict,
    )

    class Meta:
        """Meta definition for GroupedProduct."""

        verbose_name = _("Grouped Product")
        verbose_name_plural = _("Grouped Products")

    def __str__(self):
        """Unicode representation of GroupedProduct."""
        return self.name


class CategoryByUrl(ProductBaseModel):
    """Model definition for Category By Url."""

    name = models.CharField(
        _("Name"),
        help_text=_("Enter the name of the category by url"),
        max_length=250,
    )
    url_path = models.ForeignKey(
        Url,
        verbose_name=_("Url path"),
        help_text=_("Select the url path"),
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    url = models.CharField(
        _("Url"),
        help_text=_("Enter the url of the category by url"),
        max_length=250,
        blank=True,
        null=True,
    )
    categories = models.ManyToManyField(
        Category,
        verbose_name=_("Category"),
        help_text=_("Select the category"),
    )

    class Meta:
        """Meta definition for Category By Url."""

        verbose_name = _("Category By Url")
        verbose_name_plural = _("Category By Urls")

    def __str__(self):
        """Unicode representation of Category By Url."""
        return self.name
