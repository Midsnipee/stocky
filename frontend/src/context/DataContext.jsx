import { createContext, useContext, useMemo, useState } from 'react';
import dayjs from 'dayjs';
import { demoData } from '../utils/demoData.js';
import { computeStockMetrics } from '../utils/metrics.js';

const DataContext = createContext();

export function DataProvider({ children }) {
  const [data, setData] = useState(demoData);

  const contextValue = useMemo(() => {
    const metrics = computeStockMetrics(data);

    const updateOrderStatus = (orderId, status) => {
      setData((prev) => ({
        ...prev,
        orders: prev.orders.map((order) =>
          order.id === orderId ? { ...order, status } : order
        )
      }));
    };

    const addActivity = (entry) => {
      setData((prev) => ({
        ...prev,
        activity: [entry, ...prev.activity]
      }));
    };

    const addAssignment = (assignment) => {
      setData((prev) => ({
        ...prev,
        assignments: [assignment, ...prev.assignments]
      }));
    };

    const persistPreference = (key, value) => {
      window.localStorage.setItem(key, JSON.stringify(value));
    };

    const loadPreference = (key, fallback) => {
      const raw = window.localStorage.getItem(key);
      if (!raw) return fallback;
      try {
        return JSON.parse(raw);
      } catch (error) {
        console.warn('Unable to parse preference', error);
        return fallback;
      }
    };

    return {
      data,
      metrics,
      updateOrderStatus,
      addActivity,
      addAssignment,
      persistPreference,
      loadPreference,
      dayjs
    };
  }, [data]);

  return <DataContext.Provider value={contextValue}>{children}</DataContext.Provider>;
}

export const useData = () => useContext(DataContext);
