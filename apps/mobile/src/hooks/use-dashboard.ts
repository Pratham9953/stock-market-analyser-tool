import { useQuery } from '@tanstack/react-query';
import { api } from '../lib/api';
import { useSessionStore } from '../store/session-store';

export const useDashboard = () => {
  const setSummary = useSessionStore((state) => state.setSummary);
  return useQuery({
    queryKey: ['dashboard-summary'],
    queryFn: async () => {
      const summary = await api.getDashboardSummary();
      setSummary(summary);
      return summary;
    },
    refetchInterval: 5000
  });
};
