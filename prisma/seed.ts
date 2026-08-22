import { PrismaClient, UserRole, StoreStatus, ProductStatus, OrderStatus, PaymentStatus, PaymentMethod, ShipmentStatus, AddressType, DiscountType, ReviewStatus, NotificationType } from '@prisma/client';

const prisma = new PrismaClient();

async function main() {
  console.log('🌱 Seeding Garuda E-Commerce & Marketplace Database...');

  // 1. Clean existing data (respecting foreign key relationships)
  console.log('🧹 Cleaning existing records...');
  await prisma.notification.deleteMany();
  await prisma.auditLog.deleteMany();
  await prisma.couponUsage.deleteMany();
  await prisma.coupon.deleteMany();
  await prisma.reviewImage.deleteMany();
  await prisma.review.deleteMany();
  await prisma.refund.deleteMany();
  await prisma.payment.deleteMany();
  await prisma.shipment.deleteMany();
  await prisma.orderStatusLog.deleteMany();
  await prisma.orderAddress.deleteMany();
  await prisma.orderItem.deleteMany();
  await prisma.order.deleteMany();
  await prisma.wishlistItem.deleteMany();
  await prisma.cartItem.deleteMany();
  await prisma.cart.deleteMany();
  await prisma.productTag.deleteMany();
  await prisma.tag.deleteMany();
  await prisma.productImage.deleteMany();
  await prisma.productVariant.deleteMany();
  await prisma.product.deleteMany();
  await prisma.category.deleteMany();
  await prisma.store.deleteMany();
  await prisma.session.deleteMany();
  await prisma.address.deleteMany();
  await prisma.userProfile.deleteMany();
  await prisma.user.deleteMany();

  // 2. Create Users
  console.log('👤 Creating Users & Profiles...');
  const adminUser = await prisma.user.create({
    data: {
      email: 'admin@garuda.local',
      passwordHash: '$2a$12$e6xM82i2aO876c4rA7eP.e3Yd3vM6u7s4x1tY3A6t8eK0o2c3g2m', // mock hashed password
      firstName: 'Garuda',
      lastName: 'Administrator',
      role: UserRole.SUPER_ADMIN,
      isEmailVerified: true,
      profile: {
        create: {
          bio: 'System Administrator for Garuda Marketplace Platform',
          companyName: 'Garuda Technologies Inc.',
        },
      },
    },
  });

  const sellerUser1 = await prisma.user.create({
    data: {
      email: 'tech_store@garuda.local',
      passwordHash: '$2a$12$e6xM82i2aO876c4rA7eP.e3Yd3vM6u7s4x1tY3A6t8eK0o2c3g2m',
      firstName: 'Arjun',
      lastName: 'Mehta',
      role: UserRole.SELLER,
      isEmailVerified: true,
      phone: '+919876543210',
      profile: {
        create: {
          bio: 'Authorized electronics vendor and premium accessories seller.',
          companyName: 'Apex Digital Solutions Ltd.',
          taxId: 'GSTIN27AABCU9603R1ZM',
        },
      },
    },
  });

  const sellerUser2 = await prisma.user.create({
    data: {
      email: 'apparel_store@garuda.local',
      passwordHash: '$2a$12$e6xM82i2aO876c4rA7eP.e3Yd3vM6u7s4x1tY3A6t8eK0o2c3g2m',
      firstName: 'Priya',
      lastName: 'Sharma',
      role: UserRole.SELLER,
      isEmailVerified: true,
      phone: '+919876543211',
      profile: {
        create: {
          bio: 'Curated modern and traditional sustainable fashion collections.',
          companyName: 'Vogue Loom Apparels',
          taxId: 'GSTIN29AAACA1234Q1Z5',
        },
      },
    },
  });

  const customerUser = await prisma.user.create({
    data: {
      email: 'customer@garuda.local',
      passwordHash: '$2a$12$e6xM82i2aO876c4rA7eP.e3Yd3vM6u7s4x1tY3A6t8eK0o2c3g2m',
      firstName: 'Rahul',
      lastName: 'Verma',
      role: UserRole.CUSTOMER,
      isEmailVerified: true,
      phone: '+919812345678',
      profile: {
        create: {
          bio: 'Tech enthusiast and avid reader.',
        },
      },
      addresses: {
        create: [
          {
            type: AddressType.BOTH,
            fullName: 'Rahul Verma',
            phone: '+919812345678',
            street1: 'Flat 402, Skyline Residency',
            street2: 'Indiranagar 100ft Road',
            city: 'Bengaluru',
            state: 'Karnataka',
            postalCode: '560038',
            country: 'IN',
            isDefault: true,
          },
        ],
      },
    },
  });

  // 3. Create Stores
  console.log('🏬 Creating Stores...');
  const techStore = await prisma.store.create({
    data: {
      ownerId: sellerUser1.id,
      name: 'Garuda Tech Official Store',
      slug: 'garuda-tech-official',
      description: 'The official destination for high performance hardware, drones, and premium audio.',
      logoUrl: 'https://images.unsplash.com/photo-1519389950473-47ba0277781c?w=200',
      bannerUrl: 'https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=1200',
      status: StoreStatus.ACTIVE,
      contactEmail: 'contact@garudatech.com',
      contactPhone: '+919876543210',
      rating: 4.85,
      ratingCount: 142,
    },
  });

  const fashionStore = await prisma.store.create({
    data: {
      ownerId: sellerUser2.id,
      name: 'Vogue Loom Studio',
      slug: 'vogue-loom-studio',
      description: 'Handcrafted sustainable fashion and modern daily wear.',
      logoUrl: 'https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=200',
      bannerUrl: 'https://images.unsplash.com/photo-1445205170230-053b83016050?w=1200',
      status: StoreStatus.ACTIVE,
      contactEmail: 'hello@vogueloom.com',
      contactPhone: '+919876543211',
      rating: 4.70,
      ratingCount: 95,
    },
  });

  // 4. Create Hierarchical Categories
  console.log('📁 Creating Category Tree...');
  const electronics = await prisma.category.create({
    data: {
      name: 'Electronics',
      slug: 'electronics',
      description: 'Gadgets, Computers, Drones, and Audio Devices',
      level: 0,
      imageUrl: 'https://images.unsplash.com/photo-1498049794561-7780e7231661?w=400',
    },
  });

  const audioCategory = await prisma.category.create({
    data: {
      name: 'Headphones & Audio',
      slug: 'headphones-and-audio',
      description: 'Noise Cancelling Headphones, Earbuds, and Studio Monitors',
      parentId: electronics.id,
      level: 1,
    },
  });

  const dronesCategory = await prisma.category.create({
    data: {
      name: 'Drones & Robotics',
      slug: 'drones-and-robotics',
      description: 'Commercial and Recreational Aerial Drones',
      parentId: electronics.id,
      level: 1,
    },
  });

  const fashion = await prisma.category.create({
    data: {
      name: 'Fashion & Apparel',
      slug: 'fashion-and-apparel',
      description: 'Men & Women Clothing, Footwear, and Accessories',
      level: 0,
    },
  });

  const mensWear = await prisma.category.create({
    data: {
      name: "Men's Jackets & Outerwear",
      slug: 'mens-jackets-outerwear',
      parentId: fashion.id,
      level: 1,
    },
  });

  // 5. Create Tags
  console.log('🏷️ Creating Tags...');
  const tagWireless = await prisma.tag.create({ data: { name: 'Wireless', slug: 'wireless' } });
  const tagNoiseCancelling = await prisma.tag.create({ data: { name: 'Noise Cancelling', slug: 'noise-cancelling' } });
  const tagPro = await prisma.tag.create({ data: { name: 'Pro Series', slug: 'pro-series' } });
  const tag4K = await prisma.tag.create({ data: { name: '4K Camera', slug: '4k-camera' } });

  // 6. Create Products with Variants & Images
  console.log('📦 Creating Products and Variants...');

  // Product 1: Garuda Apex Noise-Cancelling Headphones
  const headphoneProduct = await prisma.product.create({
    data: {
      storeId: techStore.id,
      categoryId: audioCategory.id,
      title: 'Garuda Apex Pro Wireless ANC Headphones',
      slug: 'garuda-apex-pro-wireless-anc-headphones',
      description: 'Flagship studio-grade wireless noise cancelling headphones with 50-hour battery life and spatial audio calibration.',
      basePrice: 299.99,
      compareAtPrice: 349.99,
      currency: 'USD',
      sku: 'GAPX-ANC-001',
      status: ProductStatus.PUBLISHED,
      isFeatured: true,
      weight: 0.28,
      details: {
        batteryLifeHours: 50,
        bluetoothVersion: '5.4',
        codecSupport: ['LDAC', 'AAC', 'SBC', 'aptX Lossless'],
        warrantyYears: 2,
      },
      images: {
        create: [
          {
            url: 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800',
            altText: 'Garuda Apex Pro Headphones Front View',
            displayOrder: 0,
            isThumbnail: true,
          },
          {
            url: 'https://images.unsplash.com/photo-1484704849700-f032a568e944?w=800',
            altText: 'Garuda Apex Pro Headphones Angled View',
            displayOrder: 1,
          },
        ],
      },
      variants: {
        create: [
          {
            title: 'Midnight Black',
            sku: 'GAPX-ANC-BLK',
            price: 299.99,
            compareAtPrice: 349.99,
            costPrice: 160.00,
            stockQuantity: 45,
            lowStockThreshold: 10,
            attributes: { color: 'Midnight Black', finish: 'Matte' },
          },
          {
            title: 'Silver Platinum',
            sku: 'GAPX-ANC-PLT',
            price: 299.99,
            compareAtPrice: 349.99,
            costPrice: 160.00,
            stockQuantity: 28,
            lowStockThreshold: 5,
            attributes: { color: 'Silver Platinum', finish: 'Brushed Metallic' },
          },
        ],
      },
      tags: {
        create: [
          { tagId: tagWireless.id },
          { tagId: tagNoiseCancelling.id },
          { tagId: tagPro.id },
        ],
      },
    },
    include: { variants: true },
  });

  // Product 2: Garuda Falcon 4K Quadcopter Drone
  const droneProduct = await prisma.product.create({
    data: {
      storeId: techStore.id,
      categoryId: dronesCategory.id,
      title: 'Garuda Falcon X4 Aerial Drone (4K/60fps HDR)',
      slug: 'garuda-falcon-x4-aerial-drone',
      description: 'Ultra-lightweight high stability drone with 3-axis mechanical gimbal, omnidirectional obstacle avoidance, and 12km transmission range.',
      basePrice: 899.00,
      compareAtPrice: 999.00,
      currency: 'USD',
      sku: 'GFRC-FLC-X4',
      status: ProductStatus.PUBLISHED,
      isFeatured: true,
      weight: 0.59,
      details: {
        flightTimeMinutes: 38,
        videoResolution: '4K 60fps',
        maxRangeKm: 12,
        sensorSize: '1-inch CMOS',
      },
      images: {
        create: [
          {
            url: 'https://images.unsplash.com/photo-1527977966376-1c8408f9f108?w=800',
            altText: 'Garuda Falcon X4 Drone in flight',
            displayOrder: 0,
            isThumbnail: true,
          },
        ],
      },
      variants: {
        create: [
          {
            title: 'Standard Flight Pack (1 Battery)',
            sku: 'GFRC-FLC-STD',
            price: 899.00,
            compareAtPrice: 999.00,
            costPrice: 550.00,
            stockQuantity: 15,
            lowStockThreshold: 3,
            attributes: { package: 'Standard', batteries: 1 },
          },
          {
            title: 'Fly More Combo (3 Batteries + Carry Bag + Hub)',
            sku: 'GFRC-FLC-COMBO',
            price: 1149.00,
            compareAtPrice: 1299.00,
            costPrice: 680.00,
            stockQuantity: 20,
            lowStockThreshold: 5,
            attributes: { package: 'Fly More Combo', batteries: 3, includeBag: true },
          },
        ],
      },
      tags: {
        create: [
          { tagId: tagWireless.id },
          { tagId: tag4K.id },
          { tagId: tagPro.id },
        ],
      },
    },
    include: { variants: true },
  });

  // 7. Create Coupons
  console.log('🎟️ Creating Coupons...');
  const promoCoupon = await prisma.coupon.create({
    data: {
      code: 'GARUDA20',
      description: '20% off on all tech and fashion orders',
      discountType: DiscountType.PERCENTAGE,
      discountValue: 20.00,
      minOrderAmount: 100.00,
      maxDiscountAmount: 150.00,
      usageLimit: 500,
      usageCount: 1,
      startsAt: new Date(),
      expiresAt: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000), // 30 days
      isActive: true,
    },
  });

  // 8. Create Sample Order & Fulfillment Flow
  console.log('🛒 Creating Sample Order, Payment, and Shipment...');
  const orderNumber = 'GAR-2026-000101';
  const selectedVariant = headphoneProduct.variants[0];
  const itemPrice = selectedVariant.price;
  const quantity = 1;
  const subtotal = itemPrice;
  const discountAmount = Number(subtotal) * 0.2; // 20% discount
  const taxAmount = (Number(subtotal) - discountAmount) * 0.18; // 18% tax
  const shippingAmount = 0.00;
  const totalAmount = Number(subtotal) - discountAmount + taxAmount + shippingAmount;

  const sampleOrder = await prisma.order.create({
    data: {
      orderNumber,
      customerId: customerUser.id,
      status: OrderStatus.CONFIRMED,
      subtotal,
      discountAmount,
      taxAmount,
      shippingAmount,
      totalAmount,
      currency: 'USD',
      couponId: promoCoupon.id,
      notes: 'Please leave package with concierge if unavailable.',
      address: {
        create: {
          shippingFullName: 'Rahul Verma',
          shippingPhone: '+919812345678',
          shippingStreet1: 'Flat 402, Skyline Residency',
          shippingStreet2: 'Indiranagar 100ft Road',
          shippingCity: 'Bengaluru',
          shippingState: 'Karnataka',
          shippingPostalCode: '560038',
          shippingCountry: 'IN',
          billingFullName: 'Rahul Verma',
          billingPhone: '+919812345678',
          billingStreet1: 'Flat 402, Skyline Residency',
          billingStreet2: 'Indiranagar 100ft Road',
          billingCity: 'Bengaluru',
          billingState: 'Karnataka',
          billingPostalCode: '560038',
          billingCountry: 'IN',
        },
      },
      items: {
        create: [
          {
            storeId: techStore.id,
            productId: headphoneProduct.id,
            variantId: selectedVariant.id,
            productTitle: headphoneProduct.title,
            variantTitle: selectedVariant.title,
            sku: selectedVariant.sku,
            unitPrice: itemPrice,
            quantity,
            totalPrice: itemPrice,
          },
        ],
      },
      payments: {
        create: [
          {
            transactionId: 'TXN_GARUDA_987654321',
            method: PaymentMethod.CREDIT_CARD,
            status: PaymentStatus.COMPLETED,
            amount: totalAmount,
            currency: 'USD',
            gatewayResponse: {
              gateway: 'Stripe',
              cardBrand: 'Visa',
              last4: '4242',
              receiptUrl: 'https://pay.garuda.local/receipts/txn_987654321',
            },
            paidAt: new Date(),
          },
        ],
      },
      shipments: {
        create: [
          {
            storeId: techStore.id,
            carrier: 'BlueDart Express',
            trackingNumber: 'BLUEDART-8823910293',
            status: ShipmentStatus.PICKED_UP,
            shippedAt: new Date(),
            estimatedDelivery: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000),
          },
        ],
      },
      statusLogs: {
        create: [
          {
            fromStatus: null,
            toStatus: OrderStatus.PENDING,
            reason: 'Order placed by customer',
          },
          {
            fromStatus: OrderStatus.PENDING,
            toStatus: OrderStatus.CONFIRMED,
            reason: 'Payment successfully captured via Stripe',
          },
        ],
      },
      couponUsage: {
        create: {
          couponId: promoCoupon.id,
          userId: customerUser.id,
          discountApplied: discountAmount,
        },
      },
    },
    include: {
      items: true,
    },
  });

  // 9. Create Product Review
  console.log('⭐ Creating Product Review...');
  await prisma.review.create({
    data: {
      productId: headphoneProduct.id,
      userId: customerUser.id,
      orderItemId: sampleOrder.items[0].id,
      rating: 5,
      title: 'Spectacular sound quality and battery life!',
      comment: 'The active noise cancellation blocks out ambient office noise effortlessly. Very comfortable over the ear for long working sessions.',
      status: ReviewStatus.APPROVED,
      helpfulCount: 8,
    },
  });

  // 10. Create Notification & Audit Log
  console.log('🔔 Creating Notification & Audit Log...');
  await prisma.notification.create({
    data: {
      userId: customerUser.id,
      title: 'Order Confirmed!',
      message: `Your order #${orderNumber} has been confirmed and is being prepped for dispatch.`,
      type: NotificationType.ORDER_STATUS,
      linkUrl: `/orders/${orderNumber}`,
    },
  });

  await prisma.auditLog.create({
    data: {
      userId: adminUser.id,
      action: 'SYSTEM_BOOTSTRAP_SEED',
      entityType: 'SYSTEM',
      changes: {
        seededAt: new Date().toISOString(),
        tablesSeeded: 24,
      },
    },
  });

  console.log('✅ Garuda Database seeding completed successfully!');
}

main()
  .catch((e) => {
    console.error('❌ Seeding error:', e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
