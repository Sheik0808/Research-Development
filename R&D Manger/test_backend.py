import os
import io
import pandas as pd
from app import app, get_db_connection

def test_upload_excel_robustness():
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['role'] = 'admin'

        # Case 1: With Department Name
        data1 = {'Paper Title': ['Test P1'], 'Author Name': ['A1'], 'Department Name': ['CSBS'], 'Journal Name': ['J1'], 'Publication Type': ['Journal'], 'Status': ['Published']}
        df1 = pd.DataFrame(data1)
        excel1 = io.BytesIO()
        df1.to_excel(excel1, index=False, engine='openpyxl')
        excel1.seek(0)
        resp1 = client.post('/upload_excel', data={'excel_file': (excel1, 'test1.xlsx')}, content_type='multipart/form-data')
        print(f"Case 1 (With Dept) Response: {resp1.get_json()}")

        # Case 2: Without Department Name (The Crash Case)
        data2 = {'Paper Title': ['Test P2'], 'Author Name': ['A2'], 'Journal Name': ['J2'], 'Publication Type': ['Journal'], 'Status': ['Published']}
        df2 = pd.DataFrame(data2)
        excel2 = io.BytesIO()
        df2.to_excel(excel2, index=False, engine='openpyxl')
        excel2.seek(0)
        resp2 = client.post('/upload_excel', data={'excel_file': (excel2, 'test2.xlsx')}, content_type='multipart/form-data')
        print(f"Case 2 (No Dept) Response: {resp2.get_json()}")
        
        # Case 3: Title Filtering
        data3 = {'Paper Title': ['Deep Learning Research'], 'Author Name': ['A3'], 'Journal Name': ['J3'], 'Publication Type': ['Journal'], 'Status': ['Accepted']}
        df3 = pd.DataFrame(data3)
        excel3 = io.BytesIO()
        df3.to_excel(excel3, index=False, engine='openpyxl')
        excel3.seek(0)
        client.post('/upload_excel', data={'excel_file': (excel3, 'test3.xlsx')}, content_type='multipart/form-data')
        
        # Test the filter
        resp_filtered = client.get('/excel_dashboard?title=Deep', headers={'X-Requested-With': 'XMLHttpRequest'})
        if 'Deep Learning Research' in resp_filtered.get_data(as_text=True):
            print("OK: Title filtering works.")
        else:
            print("FAIL: Title filtering failed.")
            
        # Test Status filter for 'Accepted'
        resp_status = client.get('/excel_dashboard?status=Accepted', headers={'X-Requested-With': 'XMLHttpRequest'})
        if 'Accepted' in resp_status.get_data(as_text=True):
            print("OK: Status 'Accepted' filtering works.")
        else:
            print("FAIL: Status 'Accepted' filtering failed.")

def test_template_rendering():
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['role'] = 'admin'
            
        # Test view_journals
        response = client.get('/view_journals')
        if response.status_code == 200:
            content = response.data.decode('utf-8')
            # Check for aligned headers and data cells (this is indirect but useful)
            if 'Dept' in content and 'Category' in content:
                print("OK: /view_journals rendered correctly.")
            else:
                print("FAIL: /view_journals rendering issue.")
        else:
            print(f"FAIL: /view_journals returned status {response.status_code}")

def test_filtered_stats():
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['role'] = 'admin'
            
        # 1. Total stats (no filter)
        response = client.get('/excel_dashboard')
        data = response.data.decode('utf-8')
        print(f"Total Stats present: {'Total' in data}")
        
        # 2. Filter by department
        # Assuming we have some data for 'CSBS' from previous test
        response = client.get('/excel_dashboard?dept=CSBS')
        content = response.data.decode('utf-8')
        
        # Check if stats cards contain the filtered count
        if 'Total' in content:
            print("OK: Stats overview rendered in filtered result.")
        else:
            print("FAIL: Stats overview missing in filtered result.")

        # 3. Check Department Sorting
        resp_sorted = client.get('/excel_dashboard')
        page_content = resp_sorted.get_data(as_text=True)
        # Check if 'AIDS' comes before 'CSBS' in the table (basic check)
        aids_pos = page_content.find('AIDS')
        csbs_pos = page_content.find('CSBS')
        if aids_pos != -1 and csbs_pos != -1 and aids_pos < csbs_pos:
            print("OK: Department sorting (A-Z) is active.")
        else:
            print("FAIL: Department sorting check failed.")
            
        # 4. Check Dept Summary
        if 'Department Wise Summary' in page_content:
            print("OK: Department Wise Summary section is present.")
        else:
            print("FAIL: Department Wise Summary section missing.")

if __name__ == '__main__':
    test_upload_excel_robustness()
    test_template_rendering()
    test_filtered_stats()
