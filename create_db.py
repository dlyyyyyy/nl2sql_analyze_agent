import sqlite3
import random
from datetime import datetime, timedelta

# 连接数据库
conn = sqlite3.connect('sales.db')
cursor = conn.cursor()

# 删除旧表（如果存在）
cursor.execute('DROP TABLE IF EXISTS orders')
cursor.execute('DROP TABLE IF EXISTS customers')

# ========== 创建客户表 ==========
cursor.execute('''
CREATE TABLE customers (
    id INTEGER PRIMARY KEY,
    name TEXT,
    industry TEXT,
    city TEXT,
    credit_rating INTEGER
)
''')

# 客户种子数据（40个客户覆盖不同行业和城市）
customer_names = [
    '北京政务中心', '上海市政府', '广州住建局', '深圳规划局',
    '恒大地产', '万科集团', '保利发展', '华润置地',
    '中国建筑', '中铁建设', '中交集团', '中国电建',
    '腾讯科技', '阿里巴巴', '字节跳动', '华为技术',
    '国家电网', '南方电网', '华能集团', '大唐集团',
    '北京大学', '清华大学', '浙江大学', '中山大学',
    '北京医院', '上海瑞金', '广州中山', '深圳人民医院',
    '中国移动', '中国电信', '中国联通', '中国铁塔',
    '中国石化', '中国石油', '中海油', '中化集团',
    '比亚迪', '宁德时代', '蔚来汽车', '理想汽车'
]

industries = ['政府', '地产', '制造业', '互联网', '能源', '教育', '医疗', '通信']
cities = ['北京', '上海', '广州', '深圳']

customers = []
for i, name in enumerate(customer_names):
    customers.append({
        'id': i+1,
        'name': name,
        'industry': random.choice(industries),
        'city': random.choice(cities),
        'credit_rating': random.randint(1, 5)
    })

cursor.executemany(
    'INSERT INTO customers (id, name, industry, city, credit_rating) VALUES (?, ?, ?, ?, ?)',
    [(c['id'], c['name'], c['industry'], c['city'], c['credit_rating']) for c in customers]
)

# ========== 创建订单表 ==========
cursor.execute('''
CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    order_date TEXT,
    region TEXT,
    product TEXT,
    sales_amount REAL,
    collection_amount REAL,
    overdue_days INTEGER,
    customer_id INTEGER,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
)
''')

# 生成订单数据
products = ['A产品', 'B产品', 'C产品']
regions = ['北京', '上海', '广州', '深圳']
start_date = datetime(2023, 1, 1)
orders_data = []

for i in range(400):
    # 随机选择一个客户
    customer = random.choice(customers)
    
    # 生成日期（2023-2025年）
    days_offset = random.randint(0, 1095)  # 3年
    order_date = start_date + timedelta(days=days_offset)
    
    region = customer['city']  # 客户所在地即订单区域
    product = random.choice(products)
    sales_amount = round(random.uniform(10000, 100000), 2)
    
    # 根据客户信用评级影响回款率
    base_collection_rate = {
        5: 0.95,  # 高信用 → 高回款率
        4: 0.85,
        3: 0.75,
        2: 0.65,
        1: 0.50
    }[customer['credit_rating']]
    
    # 加入随机波动
    collection_rate = max(0.3, min(1.0, base_collection_rate + random.uniform(-0.15, 0.15)))
    collection_amount = round(sales_amount * collection_rate, 2)
    
    # 逾期天数：如果回款率<70%，有一定概率逾期
    if collection_rate < 0.7:
        overdue_days = random.randint(30, 180)
    elif collection_rate < 0.85:
        overdue_days = random.randint(0, 30)
    else:
        overdue_days = 0
    
    orders_data.append({
        'id': i+1,
        'order_date': order_date.strftime('%Y-%m-%d'),
        'region': region,
        'product': product,
        'sales_amount': sales_amount,
        'collection_amount': collection_amount,
        'overdue_days': overdue_days,
        'customer_id': customer['id']
    })

cursor.executemany(
    'INSERT INTO orders (id, order_date, region, product, sales_amount, collection_amount, overdue_days, customer_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
    [(o['id'], o['order_date'], o['region'], o['product'], o['sales_amount'], o['collection_amount'], o['overdue_days'], o['customer_id']) for o in orders_data]
)

conn.commit()
conn.close()

print("✅ 两张表创建成功！")
print(f"   - customers 表: {len(customers)} 条客户数据")
print(f"   - orders 表: {len(orders_data)} 条订单数据")