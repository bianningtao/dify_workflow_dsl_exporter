#!/usr/bin/env python3
"""
初始化管理员账号脚本
用于首次运行时创建默认管理员账号
"""
import sys
import logging
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from services.user_service import user_service
from sqlalchemy import create_engine
from models.user import Base
from services.db_config_loader import get_database_url
from services.system_config_loader import get_default_admin_config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_tables():
    """创建用户相关的数据库表"""
    try:
        db_url = get_database_url()
        engine = create_engine(db_url)
        Base.metadata.create_all(engine)
        logger.info("✓ 数据库表创建成功")
        return True
    except Exception as e:
        logger.error(f"✗ 创建数据库表失败: {e}")
        return False


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("初始化管理员账号")
    print("=" * 60)
    print()
    
    # 步骤1：创建数据库表
    print("[1/2] 创建数据库表...")
    if not create_tables():
        print("\n提示：如果表已存在，请忽略此错误")
    
    # 步骤2：创建管理员账号
    print("\n[2/2] 创建管理员账号...")
    
    # 从配置文件加载默认管理员配置
    admin_config = get_default_admin_config()
    admin_email = admin_config.get('email', 'admin@example.com')
    admin_password = admin_config.get('password', 'admin123456')  # ⚠️ 生产环境请立即修改此密码
    admin_username = admin_config.get('username', '系统管理员')
    
    try:
        # 检查是否已存在管理员
        existing_admin = user_service.get_user_by_email(admin_email)
        if existing_admin:
            print(f"\n⚠ 管理员账号已存在")
            print(f"邮箱: {admin_email}")
            print(f"如需重置密码，请使用其他工具或直接修改数据库")
            return
        
        # 创建管理员账号
        admin_user = user_service.create_user(
            email=admin_email,
            password=admin_password,
            username=admin_username,
            is_admin=True
        )
        
        print("\n" + "=" * 60)
        print("✓ 管理员账号创建成功！")
        print("=" * 60)
        print()
        print("登录信息：")
        print(f"  邮箱: {admin_email}")
        print(f"  密码: {admin_password}")
        print()
        print("⚠️ 重要提示：")
        print("  1. 请立即登录并修改默认密码")
        print("  2. 请勿在生产环境使用默认密码")
        print("  3. 管理员可以在系统中创建其他用户账号")
        print()
        print("=" * 60)
        
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"✗ 创建管理员失败: {e}")
        print("=" * 60)
        logger.error(f"创建管理员失败: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()

