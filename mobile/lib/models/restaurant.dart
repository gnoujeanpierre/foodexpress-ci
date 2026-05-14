class Restaurant {
  final String id;
  final String name;
  final String description;
  final String address;
  final bool isOpen;
  final double commissionRate;

  Restaurant({
    required this.id,
    required this.name,
    required this.description,
    required this.address,
    required this.isOpen,
    required this.commissionRate,
  });

  factory Restaurant.fromJson(Map<String, dynamic> json) {
    return Restaurant(
      id: json['id'] ?? '',
      name: json['name'] ?? '',
      description: json['description'] ?? '',
      address: json['address'] ?? '',
      isOpen: json['is_open'] ?? false,
      commissionRate: (json['commission_rate'] ?? 0).toDouble(),
    );
  }
}
