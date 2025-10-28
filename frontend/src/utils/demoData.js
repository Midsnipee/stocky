import dayjs from 'dayjs';

const today = dayjs();

const categories = ['PC Portable', 'Écran', 'Dock', 'Smartphone'];

const users = [
  { id: 'u1', displayName: 'Alice Martin', email: 'alice@corp.fr', department: 'IT', site: 'Paris' },
  { id: 'u2', displayName: 'Bruno Lemaire', email: 'bruno@corp.fr', department: 'Finance', site: 'Lyon' },
  { id: 'u3', displayName: 'Claire Dubois', email: 'claire@corp.fr', department: 'RH', site: 'Paris' },
  { id: 'u4', displayName: 'David Bernard', email: 'david@corp.fr', department: 'IT', site: 'Marseille' }
];

const suppliers = [
  { id: 's1', name: 'ACME', contact: 'Jean Dupont', email: 'sales@acme.fr', phone: '01 22 33 44 55', address: 'Paris' },
  { id: 's2', name: 'Contoso', contact: 'Sophie Martin', email: 'contact@contoso.fr', phone: '01 98 76 54 32', address: 'Lyon' }
];

const items = Array.from({ length: 10 }).map((_, index) => {
  const category = categories[index % categories.length];
  const supplier = suppliers[index % suppliers.length];
  return {
    id: `item-${index + 1}`,
    name: `${category} ${index + 1}`,
    category,
    internalRef: `REF-${1000 + index}`,
    defaultSupplierId: supplier.id,
    defaultUnitPrice: 450 + index * 35,
    site: index % 2 === 0 ? 'Paris' : 'Lyon',
    lowStockThreshold: 5,
    notes: 'Matériel démo'
  };
});

const serials = [];
items.forEach((item, index) => {
  const count = 5 + (index % 3);
  for (let i = 0; i < count; i += 1) {
    const deliveredAt = today.subtract(120 - i * 10, 'day');
    serials.push({
      id: `${item.id}-SN${i + 1}`,
      itemId: item.id,
      serialNumber: `SN-${item.internalRef}-${i + 1}`,
      deliveryDate: deliveredAt.toISOString(),
      warrantyStart: deliveredAt.toISOString(),
      warrantyEnd: deliveredAt.add(2, 'year').toISOString(),
      supplierId: item.defaultSupplierId,
      purchasePrice: item.defaultUnitPrice + i * 10,
      status: i % 3 === 0 ? 'Attribué' : 'En stock',
      currentAssigneeUserId: i % 3 === 0 ? users[i % users.length].id : null,
      files: []
    });
  }
});

const assignments = serials
  .filter((serial) => serial.status === 'Attribué')
  .map((serial, index) => ({
    id: `assign-${index + 1}`,
    serialId: serial.id,
    assigneeUserId: serial.currentAssigneeUserId,
    startDate: today.subtract(index * 7, 'day').toISOString(),
    expectedReturnDate: today.add(30 - index * 3, 'day').toISOString(),
    documentFile: null,
    notes: 'Attribution de démonstration'
  }));

const quotes = Array.from({ length: 5 }).map((_, index) => ({
  id: `quote-${index + 1}`,
  supplierId: suppliers[index % suppliers.length].id,
  ref: `Q-${2024 + index}`,
  amount: 1500 + index * 500,
  currency: 'EUR',
  status: 'Demandé',
  requestedByUserId: users[index % users.length].id,
  createdAt: today.subtract(index * 5, 'day').toISOString(),
  files: []
}));

const orders = [
  {
    id: 'order-1',
    quoteId: 'quote-1',
    supplierId: 's1',
    internalRef: 'CMD-2024-001',
    status: 'Commande fournisseur faite',
    orderedAt: today.subtract(15, 'day').toISOString(),
    expectedDeliveryAt: today.add(10, 'day').toISOString(),
    files: ['Bon de commande.pdf'],
    lines: [
      { id: 'line-1', itemId: 'item-1', qty: 5, unitPrice: 650, taxRate: 0.2 },
      { id: 'line-2', itemId: 'item-2', qty: 3, unitPrice: 220, taxRate: 0.2 }
    ],
    deliveries: [
      {
        id: 'deliv-1',
        deliveryNoteRef: 'BL-4587',
        deliveredAt: today.subtract(3, 'day').toISOString(),
        qtyReceived: 4,
        files: []
      }
    ],
    comments: [
      { id: 'com-1', message: 'Livraison partielle reçue', createdAt: today.subtract(3, 'day').toISOString() }
    ]
  },
  {
    id: 'order-2',
    quoteId: 'quote-2',
    supplierId: 's2',
    internalRef: 'CMD-2024-002',
    status: 'Livré',
    orderedAt: today.subtract(35, 'day').toISOString(),
    expectedDeliveryAt: today.subtract(5, 'day').toISOString(),
    files: ['Facture.pdf'],
    lines: [
      { id: 'line-3', itemId: 'item-3', qty: 10, unitPrice: 150, taxRate: 0.2 }
    ],
    deliveries: [
      {
        id: 'deliv-2',
        deliveryNoteRef: 'BL-9654',
        deliveredAt: today.subtract(6, 'day').toISOString(),
        qtyReceived: 10,
        files: []
      }
    ],
    comments: []
  },
  {
    id: 'order-3',
    supplierId: 's1',
    internalRef: 'CMD-2024-003',
    status: 'Commande dans le circuit interne',
    orderedAt: today.subtract(5, 'day').toISOString(),
    expectedDeliveryAt: today.add(20, 'day').toISOString(),
    files: [],
    lines: [
      { id: 'line-4', itemId: 'item-4', qty: 8, unitPrice: 310, taxRate: 0.2 }
    ],
    deliveries: [],
    comments: []
  },
  {
    id: 'order-4',
    supplierId: 's2',
    internalRef: 'CMD-2024-004',
    status: 'Demandé',
    orderedAt: today.subtract(2, 'day').toISOString(),
    expectedDeliveryAt: today.add(25, 'day').toISOString(),
    files: [],
    lines: [
      { id: 'line-5', itemId: 'item-5', qty: 12, unitPrice: 420, taxRate: 0.2 }
    ],
    deliveries: [],
    comments: []
  }
];

const activity = [
  {
    id: 'act-1',
    entityType: 'order',
    entityId: 'order-1',
    action: 'Livraison partielle enregistrée',
    actorUserId: 'u1',
    at: today.subtract(3, 'day').toISOString(),
    payloadJSON: {}
  },
  {
    id: 'act-2',
    entityType: 'assignment',
    entityId: 'assign-1',
    action: 'Attribution réalisée',
    actorUserId: 'u2',
    at: today.subtract(2, 'day').toISOString(),
    payloadJSON: {}
  }
];

const alerts = [
  { id: 'alert-1', type: 'Stock bas', message: 'Dock 3 en dessous du seuil', severity: 'warning' },
  { id: 'alert-2', type: 'Garantie', message: 'PC Portable 1 expire dans 30 jours', severity: 'danger' }
];

export const demoData = {
  users,
  suppliers,
  items,
  serials,
  assignments,
  quotes,
  orders,
  activity,
  alerts
};
