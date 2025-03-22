import pandas as pd
import sqlite3


def search_fund_data(db_path, identification, start_date=None, end_date=None):
    """
    Searches for fund data in the specified database and returns a Pandas DataFrame.

    Args:
        db_path (str): Path to the SQLite database file.
        identification (str or int): The fund identification number.
        start_date (str, optional):  Start date for the search (YYYY-MM-DD). Defaults to None.
        end_date (str, optional): End date for the search (YYYY-MM-DD). Defaults to None.

    Returns:
        pandas.DataFrame: A DataFrame containing the date, unit_net_worth, and acc_net_worth.
                           Returns an empty DataFrame if no data is found or if there's an error.
    """
    fund_code = f"fund_{str(identification).zfill(6)}"
    conn = None  # Initialize conn to None
    try:
        conn = sqlite3.connect(db_path)

        # Build the SQL query dynamically based on provided dates
        query = (
            f"SELECT date, daily_return, unit_net_worth, acc_net_worth FROM {fund_code}"
        )
        conditions = []
        if start_date:
            conditions.append(f"date >= '{start_date}'")
        if end_date:
            conditions.append(f"date <= '{end_date}'")

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        # print(f"Executing SQL query: {query}") #debug
        df = pd.read_sql_query(query, conn)
        return df

    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        return pd.DataFrame()  # Return an empty DataFrame on error
    except Exception as e:
        print(f"An error occurred: {e}")
        return pd.DataFrame()  # Return empty DataFrame for other errors

    finally:
        if conn:
            conn.close()


def search_by_product_name(ccb_db_path, fund_db_path, product_name):
    """
    通过产品名称在CCB数据库中查找标识符，然后搜索对应的基金数据。

    Args:
        ccb_db_path (str): CCB数据库文件路径
        fund_db_path (str): 基金数据库文件路径
        product_name (str): 产品名称

    Returns:
        pandas.DataFrame: 包含基金数据的DataFrame
    """
    try:
        # 连接CCB数据库查找标识符
        conn = sqlite3.connect(ccb_db_path)
        query = "SELECT identification FROM CCB_finance_products_core WHERE product_name LIKE ?"
        cursor = conn.cursor()
        cursor.execute(query, (f"%{product_name}%",))
        result = cursor.fetchone()
        conn.close()

        if result is None:
            print(f"未找到产品名称 '{product_name}' 的对应记录")
            return pd.DataFrame()

        # 获取标识符并搜索基金数据
        identification = result[0]
        # print(f"找到产品 '{product_name}' 的标识符: {identification}")
        return search_fund_data(fund_db_path, identification)

    except sqlite3.Error as e:
        print(f"数据库错误: {e}")
        return pd.DataFrame()
    except Exception as e:
        print(f"发生错误: {e}")
        return pd.DataFrame()
