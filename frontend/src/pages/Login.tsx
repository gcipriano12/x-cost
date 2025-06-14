
import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { ArrowLeft, Eye, EyeOff } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { useAuth } from '@/hooks/useAuth';
import { useTranslation } from 'react-i18next';
import { ThemeToggle } from '@/components/theme/ThemeToggle';
import { Logo } from '@/components/ui/logo';

const Login = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { login, loading, isAuthenticated } = useAuth();
  
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  });
  const [showPassword, setShowPassword] = useState(false);

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/megabill');
    }
  }, [isAuthenticated, navigate]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await login(formData.username, formData.password);
      navigate('/megabill');
    } catch (error) {
      // Error handling is done in the useAuth hook
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }));
  };

  return (
    <div className="flex min-h-screen bg-muted">
      <div className="flex flex-col w-full">
        {/* Header */}
        <header className="p-4 bg-background border-b">
          <div className="container mx-auto flex justify-between items-center">
            <Link to="/" className="flex items-center gap-2 text-foreground hover:opacity-80 transition-opacity">
              <ArrowLeft className="h-4 w-4" />
              <span>{t('login.backToHome')}</span>
            </Link>
            <ThemeToggle />
          </div>
        </header>

        {/* Main Content */}
        <main className="flex-1 flex items-center justify-center p-4">
          <Card className="w-full max-w-md shadow-lg">
            <CardHeader className="space-y-1">
              <div className="flex justify-center mb-6">
                <Logo size="lg" />
              </div>
              <CardTitle className="text-2xl text-center">
                {t('login.title')}
              </CardTitle>
              <CardDescription className="text-center">
                {t('login.subtitle')}
              </CardDescription>
            </CardHeader>
            <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="username">{t('login.form.username')}</Label>
                <Input
                  id="username"
                  name="username"
                  type="text"
                  value={formData.username}
                  onChange={handleInputChange}
                  placeholder="admin"
                  required
                  disabled={loading}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="password">{t('login.form.password')}</Label>
                <div className="relative">
                  <Input
                    id="password"
                    name="password"
                    type={showPassword ? 'text' : 'password'}
                    value={formData.password}
                    onChange={handleInputChange}
                    placeholder="••••••••"
                    required
                    disabled={loading}
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                    onClick={() => setShowPassword(!showPassword)}
                    disabled={loading}
                  >
                    {showPassword ? (
                      <EyeOff className="h-4 w-4" />
                    ) : (
                      <Eye className="h-4 w-4" />
                    )}
                  </Button>
                </div>
              </div>

              <Button 
                type="submit" 
                className="w-full" 
                disabled={loading}
              >
                {loading ? t('login.form.loggingIn') : t('login.form.login')}
              </Button>
            </form>

            <div className="mt-6 text-center space-y-2">
              <Link 
                to="/forgot-password" 
                className="text-sm text-blue-600 hover:underline"
              >
                {t('login.forgotPassword')}
              </Link>
              
              <div className="text-sm text-muted-foreground">
                {t('login.noAccount')}{' '}
                <Link to="/signup" className="text-blue-600 hover:underline">
                  {t('login.signUp')}
                </Link>
              </div>
            </div>
          </CardContent>
        </Card>
        </main>
      </div>
    </div>
  );
};

export default Login;
