export function computeStockMetrics(data) {
  const stockByCategory = data.items.reduce((acc, item) => {
    const serials = data.serials.filter(
      (serial) => serial.itemId === item.id && serial.status === 'En stock'
    );
    acc[item.category] = (acc[item.category] || 0) + serials.length;
    return acc;
  }, {});

  const lowStock = data.items
    .map((item) => {
      const count = data.serials.filter(
        (serial) => serial.itemId === item.id && serial.status === 'En stock'
      ).length;
      return { item, count };
    })
    .filter(({ item, count }) => count <= item.lowStockThreshold);

  const stockValue = data.serials.reduce(
    (total, serial) => total + (serial.purchasePrice || 0),
    0
  );

  const warrantyAlerts = data.serials.filter((serial) => {
    if (!serial.warrantyEnd) return false;
    const daysLeft = Math.ceil(
      (new Date(serial.warrantyEnd) - Date.now()) / (1000 * 60 * 60 * 24)
    );
    return daysLeft <= 90;
  });

  const recentAssignments = data.assignments
    .slice()
    .sort((a, b) => new Date(b.startDate) - new Date(a.startDate))
    .slice(0, 10);

  const pendingDeliveries = data.orders.filter(
    (order) => order.status === 'Commande fournisseur faite'
  );

  return {
    stockByCategory,
    lowStock,
    stockValue,
    warrantyAlerts,
    recentAssignments,
    pendingDeliveries
  };
}
