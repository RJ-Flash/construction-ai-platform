import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useAtom } from 'jotai'
import { toast } from 'sonner'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { persistUserAtom, persistTokenAtom } from '@/store/auth'
import { authAPI } from '@/services/api'

// Form validation schema
const registerSchema = z.object({
  full_name: z.string().min(3, { message: "Full name must be at least 3 characters" }),
  email: z.string().email({ message: "Please enter a valid email address" }),
  password: z.string().min(6, { message: "Password must be at least 6 characters" }),
  confirmPassword: z.string(),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords do not match",
  path: ["confirmPassword"],
})

type RegisterFormValues = z.infer<typeof registerSchema>

const Register = () => {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [, setUser] = useAtom(persistUserAtom)
  const [, setToken] = useAtom(persistTokenAtom)
  
  const { register, handleSubmit, formState: { errors } } = useForm<RegisterFormValues>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      full_name: '',
      email: '',
      password: '',
      confirmPassword: '',
    },
  })
  
  const onSubmit = async (data: RegisterFormValues) => {
    try {
      setLoading(true)
      
      // Extract required fields (exclude confirmPassword)
      const { full_name, email, password } = data
      
      // Call register API
      const response = await authAPI.register({ email, password, full_name })
      
      // Extract token from response
      const { access_token } = response
      
      if (!access_token) {
        throw new Error('Invalid registration response')
      }
      
      // Set token in store
      setToken(access_token)
      
      // Get user data
      const userData = await authAPI.getCurrentUser()
      
      // Set user in store
      setUser(userData)
      
      // Show success message
      toast.success('Registration successful')
      
      // Redirect to dashboard
      navigate('/')
    } catch (error) {
      console.error('Registration error:', error)
      toast.error('Registration failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }
  
  return (
    <div>
      <CardHeader className="space-y-1">
        <CardTitle className="text-2xl font-bold">Create an account</CardTitle>
        <CardDescription>
          Enter your information to create an account
        </CardDescription>
      </CardHeader>
      
      <CardContent>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="full_name">Full Name</Label>
            <Input
              id="full_name"
              type="text"
              placeholder="John Doe"
              {...register('full_name')}
            />
            {errors.full_name && (
              <p className="text-sm text-red-500">{errors.full_name.message}</p>
            )}
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              type="email"
              placeholder="your.email@example.com"
              {...register('email')}
            />
            {errors.email && (
              <p className="text-sm text-red-500">{errors.email.message}</p>
            )}
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="password">Password</Label>
            <Input
              id="password"
              type="password"
              {...register('password')}
            />
            {errors.password && (
              <p className="text-sm text-red-500">{errors.password.message}</p>
            )}
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="confirmPassword">Confirm Password</Label>
            <Input
              id="confirmPassword"
              type="password"
              {...register('confirmPassword')}
            />
            {errors.confirmPassword && (
              <p className="text-sm text-red-500">{errors.confirmPassword.message}</p>
            )}
          </div>
          
          <Button type="submit" className="w-full" disabled={loading}>
            {loading ? 'Creating account...' : 'Create Account'}
          </Button>
        </form>
      </CardContent>
      
      <CardFooter className="flex justify-center">
        <p className="text-sm text-muted-foreground">
          Already have an account?{' '}
          <Link to="/login" className="text-primary hover:underline">
            Sign in
          </Link>
        </p>
      </CardFooter>
    </div>
  )
}

export default Register
