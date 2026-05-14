class Menu {
  final String id;
  final String restaurantId;
  final String name;
  final String description;
  final int priceFcfa;
  final String category;
  final bool isAvailable;
  final int preparationTimeMin;

  Menu({
    required this.id,
    required this.restaurantId,
    required this.name,
    required this.description,
    required this.priceFcfa,
    required this.category,
    required this.isAvailable,
    required this.preparationTimeMin,
  });

  factory Menu.fromJson(Map<String, dynamic> json) {
    return Menu(
      id: json['id'] ?? '',
      restaurantId: json['restaurant_id'] ?? '',
      name: json['name'] ?? '',
      description: json['description'] ?? '',
      priceFcfa: json['price_fcfa'] ?? 0,
      category: json['category'] ?? '',
      isAvailable: json['is_available'] ?? false,
      preparationTimeMin: json['preparation_time_min'] ?? 0,
    );
  }
}
