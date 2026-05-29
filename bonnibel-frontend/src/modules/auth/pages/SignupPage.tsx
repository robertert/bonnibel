import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useNavigate } from 'react-router-dom';
import { authService } from '@/services/authService';

export const SignupPage = () => {
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);
  const [showPassword, setShowPassword] = useState(false);
  const { register, handleSubmit, formState: { isSubmitting } } = useForm();

  const onSubmit = async (data: any) => {
    setError(null);
    try {
      await authService.signup(data.email, data.password, data.name, data.surname);
      navigate('/login');
    } catch (err: any) {
      setError('Rejestracja nie powiodła się. Sprawdź dane i spróbuj ponownie.');
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-50">
      <form onSubmit={handleSubmit(onSubmit)} className="w-full max-w-sm p-6 bg-white rounded shadow-md">
        <h2 className="mb-6 text-2xl font-bold text-center text-gray-800">Rejestracja - Bonnibel</h2>

        <div className="mb-4">
          <label className="block mb-2 text-sm font-medium text-gray-700">Email:</label>
          <input type="email" {...register('email', { required: true })} className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500" style={{ borderColor: '#acc6ec', color: 'black' }} />
        </div>

        <div className="mb-4">
          <label className="block mb-2 text-sm font-medium text-gray-700">Imię:</label>
          <input {...register('name', { required: true })} className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500" style={{ borderColor: '#acc6ec', color: 'black' }} />
        </div>

        <div className="mb-4">
          <label className="block mb-2 text-sm font-medium text-gray-700">Nazwisko:</label>
          <input {...register('surname', { required: true })} className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500" style={{ borderColor: '#acc6ec', color: 'black' }} />
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

        <button type="submit" disabled={isSubmitting} className="w-full py-2 text-white bg-green-600 rounded-md hover:bg-green-700 disabled:bg-green-300">
          {isSubmitting ? 'Tworzenie konta...' : 'Zarejestruj się'}
        </button>
      </form>
    </div>
  );
};
