import 'package:dio/dio.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/restaurant.dart';
import '../models/menu.dart';

class ApiService {
  // Pour Chrome/web : localhost
  // Pour emulateur Android : 10.0.2.2
  // Pour vrai telephone : IP locale du PC (ex: 192.168.1.10)
  static const String baseUrl = 'http://localhost:8000';

  final Dio _dio = Dio(BaseOptions(
    baseUrl: baseUrl,
    connectTimeout: const Duration(seconds: 10),
    receiveTimeout: const Duration(seconds: 10),
    headers: {'Content-Type': 'application/json'},
  ));

  Future<String?> login(String phone, String password) async {
    try {
      final response = await _dio.post('/auth/login', data: {
        'username': phone,
        'password': password,
      });
      final token = response.data['access_token'];
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('token', token);
      _dio.options.headers['Authorization'] = 'Bearer ';
      return token;
    } catch (e) {
      print('Erreur login: ');
      return null;
    }
  }

  Future<List<Restaurant>> getRestaurants() async {
    try {
      final response = await _dio.get('/restaurants');
      final List data = response.data;
      return data.map((json) => Restaurant.fromJson(json)).toList();
    } catch (e) {
      print('Erreur restaurants: ');
      return [];
    }
  }

  Future<List<Menu>> getMenus(String restaurantId) async {
    try {
      final response = await _dio.get('/restaurants//menus');
      final List data = response.data;
      return data.map((json) => Menu.fromJson(json)).toList();
    } catch (e) {
      print('Erreur menus: ');
      return [];
    }
  }
}
