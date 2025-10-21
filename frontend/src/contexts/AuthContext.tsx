import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import api from '../services/api';

interface User {
  id: string;
  email: string;
  username: string;
  is_admin: boolean;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  isAuthenticated: boolean;
  isAdmin: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  // 初始化：从localStorage读取token和用户信息
  useEffect(() => {
    const storedToken = localStorage.getItem('auth_token');
    const storedUser = localStorage.getItem('user');

    if (storedToken && storedUser) {
      try {
        setToken(storedToken);
        setUser(JSON.parse(storedUser));
        
        // 验证token是否有效
        api.get('/auth/me')
          .then((response) => {
            if (response.data.success) {
              setUser(response.data.user);
            } else {
              // Token无效，清除
              handleLogout();
            }
          })
          .catch(() => {
            // Token无效或过期
            handleLogout();
          })
          .finally(() => {
            setLoading(false);
          });
      } catch (error) {
        handleLogout();
        setLoading(false);
      }
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (email: string, password: string) => {
    try {
      const response = await api.post('/auth/login', { email, password });
      
      if (response.data.success) {
        const token = response.data.token;
        const user = response.data.user;
        
        setToken(token);
        setUser(user);
        localStorage.setItem('auth_token', token);
        localStorage.setItem('user', JSON.stringify(user));
      } else {
        throw new Error(response.data.message || '登录失败');
      }
    } catch (error: any) {
      throw new Error(error.response?.data?.message || error.message || '登录失败');
    }
  };

  const handleLogout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user');
  };

  const logout = async () => {
    try {
      // 调用后端登出API
      await api.post('/auth/logout');
    } catch (error) {
      console.error('登出失败:', error);
    } finally {
      handleLogout();
    }
  };

  const value = {
    user,
    token,
    loading,
    login,
    logout,
    isAuthenticated: !!token && !!user,
    isAdmin: !!user?.is_admin,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

