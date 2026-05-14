import 'package:flutter/material.dart';
import '../models/restaurant.dart';
import '../services/api_service.dart';
import 'restaurant_detail_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  List<Restaurant> _restaurants = [];
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _loadRestaurants();
  }

  Future<void> _loadRestaurants() async {
    final restaurants = await ApiService().getRestaurants();
    setState(() {
      _restaurants = restaurants;
      _loading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Restaurants a Abidjan'),
        backgroundColor: Colors.orange,
        foregroundColor: Colors.white,
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator(color: Colors.orange))
          : _restaurants.isEmpty
              ? const Center(child: Text('Aucun restaurant trouve'))
              : ListView.builder(
                  itemCount: _restaurants.length,
                  itemBuilder: (context, index) {
                    final r = _restaurants[index];
                    return Card(
                      margin: const EdgeInsets.all(8),
                      child: ListTile(
                        leading: CircleAvatar(backgroundColor: Colors.orange, child: Text(r.name[0], style: const TextStyle(color: Colors.white))),
                        title: Text(r.name, style: const TextStyle(fontWeight: FontWeight.bold)),
                        subtitle: Text(' — % commission'),
                        trailing: r.isOpen
                            ? Container(padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4), decoration: BoxDecoration(color: Colors.green, borderRadius: BorderRadius.circular(12)), child: const Text('OUVERT', style: TextStyle(color: Colors.white, fontSize: 12)))
                            : Container(padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4), decoration: BoxDecoration(color: Colors.red, borderRadius: BorderRadius.circular(12)), child: const Text('FERME', style: TextStyle(color: Colors.white, fontSize: 12))),
                        onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => RestaurantDetailScreen(restaurant: r))),
                      ),
                    );
                  },
                ),
    );
  }
}
