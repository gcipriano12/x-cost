
import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import { useTranslation } from 'react-i18next';
import { ThemeToggle } from '@/components/theme/ThemeToggle';
import { useToast } from '@/components/ui/use-toast';
import { Eye, EyeOff, ArrowLeft } from 'lucide-react';
import { Logo } from '@/components/ui/logo';

const signupSchema = z.object({
  name: z.string().min(2, {
    message: "Name must be at least 2 characters",
  }),
  email: z.string().email({
    message: "Please enter a valid email address",
  }),
  password: z.string().min(8, {
    message: "Password must be at least 8 characters",
  }),
  confirmPassword: z.string(),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ["confirmPassword"],
});

type SignupFormValues = z.infer<typeof signupSchema>;

const Signup = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isSigningUp, setIsSigningUp] = useState(false);

  const form = useForm<SignupFormValues>({
    resolver: zodResolver(signupSchema),
    defaultValues: {
      name: '',
      email: '',
      password: '',
      confirmPassword: '',
    },
  });

  const onSubmit = async (data: SignupFormValues) => {
    try {
      setIsSigningUp(true);
      
      // This is a mock signup process - replace with your actual registration logic
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // For demo purposes - simulating signup success
      console.log('Signing up with:', data);
      
      toast({
        title: t('signup.success.title', 'Account created'),
        description: t('signup.success.description', 'Welcome to X Cost!'),
      });

      navigate('/megabill');
    } catch (error) {
      console.error('Signup error:', error);
      toast({
        title: t('signup.error.title', 'Signup failed'),
        description: t('signup.error.description', 'There was a problem creating your account. Please try again.'),
        variant: 'destructive',
      });
    } finally {
      setIsSigningUp(false);
    }
  };

  return (
    <div className="flex min-h-screen bg-muted">
      <div className="flex flex-col w-full">
        {/* Header */}
        <header className="p-4 bg-background border-b">
          <div className="container mx-auto flex justify-between items-center">
            <Link to="/" className="flex items-center gap-2 text-foreground hover:opacity-80 transition-opacity">
              <ArrowLeft className="h-4 w-4" />
              <span>{t('signup.backToHome', 'Back to home')}</span>
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
                {t('signup.title', 'Create an account')}
              </CardTitle>
              <CardDescription className="text-center">
                {t('signup.subtitle', 'Enter your details to get started with X Cost')}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Form {...form}>
                <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                  <FormField
                    control={form.control}
                    name="name"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>{t('signup.form.name', 'Full Name')}</FormLabel>
                        <FormControl>
                          <Input
                            placeholder="John Doe"
                            autoComplete="name"
                            {...field}
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="email"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>{t('signup.form.email', 'Email')}</FormLabel>
                        <FormControl>
                          <Input
                            placeholder="you@example.com"
                            type="email"
                            autoComplete="email"
                            {...field}
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="password"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>{t('signup.form.password', 'Password')}</FormLabel>
                        <FormControl>
                          <div className="relative">
                            <Input
                              placeholder="••••••••"
                              type={showPassword ? "text" : "password"}
                              autoComplete="new-password"
                              {...field}
                            />
                            <Button
                              type="button"
                              variant="ghost"
                              size="icon"
                              className="absolute right-0 top-0 h-full px-3 py-2"
                              onClick={() => setShowPassword(!showPassword)}
                              tabIndex={-1}
                            >
                              {showPassword ? (
                                <EyeOff className="h-4 w-4 text-muted-foreground" />
                              ) : (
                                <Eye className="h-4 w-4 text-muted-foreground" />
                              )}
                              <span className="sr-only">
                                {showPassword ? "Hide password" : "Show password"}
                              </span>
                            </Button>
                          </div>
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="confirmPassword"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>{t('signup.form.confirmPassword', 'Confirm Password')}</FormLabel>
                        <FormControl>
                          <div className="relative">
                            <Input
                              placeholder="••••••••"
                              type={showConfirmPassword ? "text" : "password"}
                              autoComplete="new-password"
                              {...field}
                            />
                            <Button
                              type="button"
                              variant="ghost"
                              size="icon"
                              className="absolute right-0 top-0 h-full px-3 py-2"
                              onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                              tabIndex={-1}
                            >
                              {showConfirmPassword ? (
                                <EyeOff className="h-4 w-4 text-muted-foreground" />
                              ) : (
                                <Eye className="h-4 w-4 text-muted-foreground" />
                              )}
                              <span className="sr-only">
                                {showConfirmPassword ? "Hide password" : "Show password"}
                              </span>
                            </Button>
                          </div>
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <Button
                    type="submit"
                    className="w-full mt-6 bg-XCost-blue hover:bg-blue-700 transition-colors"
                    disabled={isSigningUp}
                  >
                    {isSigningUp
                      ? t('signup.form.signingUp', 'Creating account...')
                      : t('signup.form.signUp', 'Create Account')}
                  </Button>
                </form>
              </Form>
            </CardContent>
            <CardFooter className="flex flex-col">
              <div className="text-center w-full">
                <p className="text-sm text-muted-foreground">
                  {t('signup.haveAccount', "Already have an account?")}{" "}
                  <Link
                    to="/login"
                    className="font-medium text-XCost-blue hover:underline"
                  >
                    {t('signup.login', 'Login')}
                  </Link>
                </p>
              </div>
            </CardFooter>
          </Card>
        </main>
      </div>
    </div>
  );
};

export default Signup;
