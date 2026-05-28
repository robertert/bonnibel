import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Link, useNavigate } from 'react-router-dom';
import { authService } from '@/services/authService';
import { useAuthStore } from '../store/authStore';

export const LoginPage = () => {
  const loginInStore = useAuthStore((state) => state.login);
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);
  const [showPassword, setShowPassword] = useState(false);
  
  const { register, handleSubmit, formState: { isSubmitting } } = useForm();

  const onSubmit = async (data: any) => {
    setError(null);
    try {
      // Backend oczekuje data.email, a nie data.userId
      const res = await authService.login(data.email, data.password);
      
      
      loginInStore(res.access_token, res.refresh_token, res.user_id || '');
      
      navigate('/profile'); // Od razu na projekty
    } catch (err: any) {
      setError('Nieprawidłowy adres e-mail lub hasło.');
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-50">
      <form onSubmit={handleSubmit(onSubmit)} className="w-full max-w-sm p-6 bg-white rounded shadow-md">
        <h2 className="mb-6 text-2xl font-bold text-center text-gray-800">Logowanie - Bonnibel</h2>
        
        <div className="mb-4">
          <label className="block mb-2 text-sm font-medium text-gray-700">Adres E-mail:</label>
          <input 
            type="email"
            {...register('email', { required: true })} 
            className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500" 
            style={{ borderColor: '#acc6ec', color: 'black', backgroundColor: 'white' }} 
          />
        </div>

        <div className="mb-4">
          <label className="block mb-2 text-sm font-medium text-gray-700">Hasło:</label>
          <div className="relative">
            <input 
              type={showPassword ? 'text' : 'password'} 
              {...register('password', { required: true })} 
              className="w-full px-3 py-2 pr-12 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500" 
              style={{ borderColor: '#acc6ec', color: 'black', backgroundColor: 'white' }} 
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute inset-y-0 right-0 flex items-center pr-3 text-sm text-gray-500 hover:text-gray-700"
              style={{ background: 'none', border: 'none', cursor: 'pointer' }}
            >
              {showPassword ? 'Ukryj' : 'Pokaż'}
            </button>
          </div>
        </div>

        {error && <p className="mb-4 text-sm text-red-600">{error}</p>}

        <button type="submit" disabled={isSubmitting} className="w-full py-2 text-white bg-blue-600 rounded-md hover:bg-blue-700 disabled:bg-blue-300">
          {isSubmitting ? 'Logowanie...' : 'Zaloguj się'}
        </button>
        
        <div style={{ marginTop: '15px', textAlign: 'center', fontSize: '14px', color: '#555' }}>
          Nie masz jeszcze konta?{' '}
          <Link to="/register" style={{ color: '#007bff', textDecoration: 'underline' }}>
            Zarejestruj się
          </Link>
        </div>
      </form>
    </div>
  );
};