import 'package:flutter/material.dart';
import 'home_screen.dart';
import '../services/api_service.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _phoneController = TextEditingController(text: '+22501010101');
  final _passwordController = TextEditingController(text: 'admin12');
  bool _loading = false;
  String? _error;

  Future<void> _login() async {
    setState(() { _loading = true; _error = null; });
    final token = await ApiService().login(_phoneController.text, _passwordController.text);
    setState(() { _loading = false; });

    if (token != null) {
      Navigator.pushReplacement(context, MaterialPageRoute(builder: (_) => const HomeScreen()));
    } else {
      setState(() { _error = 'Telephone ou mot de passe incorrect'; });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
n          mainAxisAlignment: MainAxisAlignment.center,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Icon(Icons.fastfood, size: 80, color: Colors.orange[800]),
            const SizedBox(height: 20),
            Text('FoodExpress-CI', textAlign: TextAlign.center,
              style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold, color: Colors.orange[900])),
            const SizedBox(height: 8),
            const Text('Livraison de repas a Abidjan', textAlign: TextAlign.center,
              style: TextStyle(fontSize: 16, color: Colors.grey)),
            const SizedBox(height: 40),
            TextField(
              controller: _phoneController,
              decoration: const InputDecoration(labelText: 'Telephone', prefixIcon: Icon(Icons.phone), border: OutlineInputBorder()),
              keyboardType: TextInputType.phone,
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _passwordController,
              decoration: const InputDecoration(labelText: 'Mot de passe', prefixIcon: Icon(Icons.lock), border: OutlineInputBorder()),
              obscureText: true,
            ),
            if (_error != null) ...[
              const SizedBox(height: 8),
              Text(_error!, style: const TextStyle(color: Colors.red)),
            ],
            const SizedBox(height: 24),
            ElevatedButton(
              onPressed: _loading ? null : _login,
              style: ElevatedButton.styleFrom(backgroundColor: Colors.orange, foregroundColor: Colors.white, padding: const EdgeInsets.symmetric(vertical: 16)),
              child: _loading ? const CircularProgressIndicator(color: Colors.white) : const Text('SE CONNECTER', style: TextStyle(fontSize: 16)),
            ),
          ],
        ),
      ),
    );
  }
}
