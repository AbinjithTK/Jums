import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';
import '../../core/providers/auth_provider.dart';
import '../../core/services/auth_service.dart';
import '../../core/theme/jumns_colors.dart';
import '../../core/theme/charcoal_decorations.dart';

class LoginScreen extends ConsumerStatefulWidget {
  const LoginScreen({super.key});

  @override
  ConsumerState<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends ConsumerState<LoginScreen> {
  final _emailCtrl = TextEditingController();
  final _passwordCtrl = TextEditingController();
  final _nameCtrl = TextEditingController();
  final _codeCtrl = TextEditingController();
  bool _isSignUp = false;
  bool _needsConfirmation = false;
  bool _obscurePassword = true;

  @override
  void dispose() {
    _emailCtrl.dispose();
    _passwordCtrl.dispose();
    _nameCtrl.dispose();
    _codeCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authNotifierProvider);

    ref.listen(authNotifierProvider, (prev, next) {
      // Router redirect handles navigation to /chat or /welcome.
      // We only need to handle the confirmation flow here.
      if (next.error == 'CONFIRM_NEEDED') {
        setState(() => _needsConfirmation = true);
      }
    });

    return Scaffold(
      backgroundColor: JumnsColors.paper,
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 32),
          child: Column(
            children: [
              const SizedBox(height: 60),
              // Logo blob
              BlobShape(
                color: JumnsColors.lavender,
                size: 80,
                child: Text('J',
                    style: GoogleFonts.gloriaHallelujah(
                        color: JumnsColors.charcoal,
                        fontSize: 40,
                        fontWeight: FontWeight.bold)),
              ),
              const SizedBox(height: 16),
              Text(
                _needsConfirmation
                    ? 'Verify Email'
                    : _isSignUp
                        ? 'Create Account'
                        : 'Welcome Back',
                style: GoogleFonts.gloriaHallelujah(
                    color: JumnsColors.charcoal,
                    fontSize: 28,
                    fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              Text(
                _needsConfirmation
                    ? 'Enter the code sent to your email'
                    : _isSignUp
                        ? 'Sign up to get started with Jumns'
                        : 'Sign in to your Jumns account',
                style: GoogleFonts.architectsDaughter(
                    color: JumnsColors.ink.withAlpha(150), fontSize: 15),
              ),
              const SizedBox(height: 32),

              // Error message
              if (authState.error != null &&
                  authState.error != 'CONFIRM_NEEDED')
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(12),
                  margin: const EdgeInsets.only(bottom: 16),
                  decoration: BoxDecoration(
                    color: JumnsColors.error.withAlpha(20),
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(
                        color: JumnsColors.error.withAlpha(60)),
                  ),
                  child: Text(authState.error!,
                      style: const TextStyle(
                          color: JumnsColors.error, fontSize: 13)),
                ),

              if (_needsConfirmation) ...[
                TextField(
                  controller: _codeCtrl,
                  keyboardType: TextInputType.number,
                  decoration: const InputDecoration(
                    labelText: 'Verification Code',
                    prefixIcon: Icon(Icons.pin),
                  ),
                ),
                const SizedBox(height: 16),
                SizedBox(
                  width: double.infinity,
                  height: 50,
                  child: ElevatedButton(
                    onPressed: authState.isLoading ? null : _confirmCode,
                    child: authState.isLoading
                        ? const SizedBox(
                            width: 20,
                            height: 20,
                            child: CircularProgressIndicator(
                                strokeWidth: 2,
                                color: JumnsColors.paper))
                        : const Text('Verify'),
                  ),
                ),
                const SizedBox(height: 12),
                TextButton(
                  onPressed: () => ref
                      .read(authNotifierProvider.notifier)
                      .resendCode(email: _emailCtrl.text.trim()),
                  child: Text('Resend Code',
                      style: GoogleFonts.architectsDaughter(
                          color: JumnsColors.charcoal,
                          fontWeight: FontWeight.w700)),
                ),
                TextButton(
                  onPressed: () =>
                      setState(() => _needsConfirmation = false),
                  child: Text('Back',
                      style: GoogleFonts.architectsDaughter(
                          color: JumnsColors.ink.withAlpha(150))),
                ),
              ] else ...[
                if (_isSignUp) ...[
                  TextField(
                    controller: _nameCtrl,
                    textCapitalization: TextCapitalization.words,
                    decoration: const InputDecoration(
                      labelText: 'Name',
                      prefixIcon: Icon(Icons.person_outline),
                    ),
                  ),
                  const SizedBox(height: 12),
                ],
                TextField(
                  controller: _emailCtrl,
                  keyboardType: TextInputType.emailAddress,
                  autocorrect: false,
                  decoration: const InputDecoration(
                    labelText: 'Email',
                    prefixIcon: Icon(Icons.email_outlined),
                  ),
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: _passwordCtrl,
                  obscureText: _obscurePassword,
                  decoration: InputDecoration(
                    labelText: 'Password',
                    prefixIcon: const Icon(Icons.lock_outline),
                    suffixIcon: IconButton(
                      icon: Icon(_obscurePassword
                          ? Icons.visibility_off
                          : Icons.visibility),
                      onPressed: () => setState(
                          () => _obscurePassword = !_obscurePassword),
                    ),
                  ),
                ),
                const SizedBox(height: 24),
                SizedBox(
                  width: double.infinity,
                  height: 50,
                  child: ElevatedButton(
                    onPressed: authState.isLoading ? null : _submit,
                    child: authState.isLoading
                        ? const SizedBox(
                            width: 20,
                            height: 20,
                            child: CircularProgressIndicator(
                                strokeWidth: 2,
                                color: JumnsColors.paper))
                        : Text(_isSignUp ? 'Sign Up' : 'Sign In'),
                  ),
                ),
                const SizedBox(height: 16),
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text(
                      _isSignUp
                          ? 'Already have an account? '
                          : "Don't have an account? ",
                      style: GoogleFonts.architectsDaughter(
                          color: JumnsColors.ink.withAlpha(150),
                          fontSize: 14),
                    ),
                    GestureDetector(
                      onTap: () => setState(() => _isSignUp = !_isSignUp),
                      child: Text(
                        _isSignUp ? 'Sign In' : 'Sign Up',
                        style: GoogleFonts.architectsDaughter(
                            color: JumnsColors.charcoal,
                            fontSize: 14,
                            fontWeight: FontWeight.w700,
                            decoration: TextDecoration.underline),
                      ),
                    ),
                  ],
                ),
                if (!_isSignUp) ...[
                  const SizedBox(height: 12),
                  TextButton(
                    onPressed: _forgotPassword,
                    child: Text('Forgot Password?',
                        style: GoogleFonts.architectsDaughter(
                            color: JumnsColors.ink.withAlpha(150),
                            fontSize: 13)),
                  ),
                ],
              ],
              const SizedBox(height: 32),
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  TextButton(
                    onPressed: () {},
                    child: Text('Privacy Policy',
                        style: GoogleFonts.architectsDaughter(
                            color: JumnsColors.ink.withAlpha(100),
                            fontSize: 11)),
                  ),
                  Text('·',
                      style: TextStyle(
                          color: JumnsColors.ink.withAlpha(100))),
                  TextButton(
                    onPressed: () {},
                    child: Text('Terms of Service',
                        style: GoogleFonts.architectsDaughter(
                            color: JumnsColors.ink.withAlpha(100),
                            fontSize: 11)),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _submit() {
    final email = _emailCtrl.text.trim();
    final password = _passwordCtrl.text;
    if (email.isEmpty || password.isEmpty) return;

    if (_isSignUp) {
      ref.read(authNotifierProvider.notifier).signUp(
            email: email,
            password: password,
            name: _nameCtrl.text.trim().isEmpty
                ? null
                : _nameCtrl.text.trim(),
          );
    } else {
      ref.read(authNotifierProvider.notifier).signIn(
            email: email,
            password: password,
          );
    }
  }

  void _confirmCode() async {
    final code = _codeCtrl.text.trim();
    if (code.isEmpty) return;

    final success = await ref
        .read(authNotifierProvider.notifier)
        .confirmSignUp(email: _emailCtrl.text.trim(), code: code);

    if (success && mounted) {
      ref.read(authNotifierProvider.notifier).signIn(
            email: _emailCtrl.text.trim(),
            password: _passwordCtrl.text,
          );
    }
  }

  void _forgotPassword() {
    final email = _emailCtrl.text.trim();
    if (email.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Enter your email first')),
      );
      return;
    }
    ref
        .read(authNotifierProvider.notifier)
        .forgotPassword(email: email);
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
          content: Text('Password reset code sent to your email')),
    );
  }
}
