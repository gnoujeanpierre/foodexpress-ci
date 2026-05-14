import 'package:flutter/material.dart';
import '../models/restaurant.dart';
import '../models/menu.dart';
import '../services/api_service.dart';

class RestaurantDetailScreen extends StatefulWidget {
  final Restaurant restaurant;
  const RestaurantDetailScreen({super.key, required this.restaurant});

  @override
  State<RestaurantDetailScreen> createState() => _RestaurantDetailScreenState();
}

class _RestaurantDetailScreenState extends State<RestaurantDetailScreen> {
  List<Menu> _menus = [];
  bool _loading = true;
  final Map<String, int> _cart = {};

  @override
  void initState() {
    super.initState();
    _loadMenus();
  }

  Future<void> _loadMenus() async {
    final menus = await ApiService().getMenus(widget.restaurant.id);
    setState(() {
      _menus = menus;
      _loading = false;
    });
  }

  int get _total {
    int sum = 0;
    _cart.forEach((id, qty) {
      final menu = _menus.firstWhere((m) => m.id == id);
      sum += menu.priceFcfa * qty;
    });
    return sum;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(widget.restaurant.name), backgroundColor: Colors.orange, foregroundColor: Colors.white),
      body: Column(
        children: [
          Container(
            padding: const EdgeInsets.all(16),
            color: Colors.orange[50],
            child: Column(
n              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(widget.restaurant.description, style: const TextStyle(fontSize: 16)),
                const SizedBox(height: 4),
                Text(widget.restaurant.address, style: const TextStyle(color: Colors.grey)),
              ],
            ),
          ),
          Expanded(
            child: _loading
                ? const Center(child: CircularProgressIndicator(color: Colors.orange))
                : _menus.isEmpty
                    ? const Center(child: Text('Aucun menu disponible'))
                    : ListView.builder(
                        itemCount: _menus.length,
                        itemBuilder: (context, index) {
                          final m = _menus[index];
                          final qty = _cart[m.id] ?? 0;
                          return ListTile(
                            title: Text(m.name, style: const TextStyle(fontWeight: FontWeight.bold)),
                            subtitle: Text(' —  min'),
                            trailing: Row(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                Text(' FCFA', style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.orange)),
                                const SizedBox(width: 8),
                                if (qty > 0)
                                  IconButton(icon: const Icon(Icons.remove_circle, color: Colors.red), onPressed: () => setState(() { _cart[m.id] = qty - 1; if (_cart[m.id] == 0) _cart.remove(m.id); })),
                                if (qty > 0) Text('', style: const TextStyle(fontWeight: FontWeight.bold)),
                                IconButton(icon: const Icon(Icons.add_circle, color: Colors.green), onPressed: () => setState(() { _cart[m.id] = qty + 1; })),
                              ],
                            ),
                          );
                        },
                      ),
          ),
          if (_cart.isNotEmpty)
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(color: Colors.orange[800], boxShadow: [BoxShadow(color: Colors.black26, blurRadius: 8)]),
              child: SafeArea(
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(' article(s)', style: const TextStyle(color: Colors.white)),
                    Text('Total:  FCFA', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 18)),
                  ],
                ),
              ),
            ),
        ],
      ),
    );
  }
}
