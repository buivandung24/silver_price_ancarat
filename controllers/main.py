from odoo import http
from odoo.http import request
import requests

class SilverPriceController(http.Controller):

    @http.route('/banggia', type='http', auth='public', website=True)
    def silver_price(self, **kw):
        api_url_silver = "https://giabac.ancarat.com/api/price-data"
        api_url_gold = "https://giavang.ancarat.com/api/price-data"
        sections = []
        current_section = None
        last_update = ""
        vat_note = ""
        hotline = ""

        try:
            response_silver = requests.get(api_url_silver, timeout=300)
            response_gold = requests.get(api_url_gold, timeout=300)

            if response_silver.status_code == 200 and response_gold.status_code == 200:
                data_silver = response_silver.json()
                data_gold = response_gold.json()

                # Tách phần cuối của API (3 dòng meta)
                meta = data_silver[-3:]
                data_silver = data_silver[:-3]  # bỏ 3 dòng cuối khỏi phần sản phẩm
                data_gold = data_gold[:-3]

                # Dòng thời gian
                if len(meta[0]) >= 3 and meta[0][2]:
                    last_update = meta[0][2]
                # Dòng ghi chú thuế
                if len(meta[1]) >= 1:
                    vat_note = meta[1][0]
                # Dòng hotline
                if len(meta[2]) >= 1:
                    hotline = meta[2][0]

                # nối chuỗi JSON
                data = []
                data.extend(data_gold)
                data.extend(data_silver)

                # Xử lý dữ liệu chính
                for row in data:
                    if len(row) > 3:
                        # loại bỏ cột 4 và 5
                        row = row[:3]

                    if len(row) == 1 and row[0]:
                        # tiêu đề nhóm
                        current_section = {
                            'title': row[0],
                            'items': []
                        }
                        sections.append(current_section)
                    elif row[0] and row[1] == "" and row[2] == "":
                        # tiêu đề nhóm
                        current_section = {
                            'title': row[0],
                            'items': []
                        }
                        sections.append(current_section)
                    elif current_section:
                        name, sell, buy = row
                        # bỏ qua dòng trống
                        if not name and not sell and not buy:
                            continue
                        current_section['items'].append({
                            'name': name,
                            'sell': sell,
                            'buy': buy
                        })

            else:
                sections = [{'title': 'Lỗi tải dữ liệu', 'items': []}]
        except Exception as e:
            sections = [{'title': 'Lỗi kết nối API', 'items': []}]
            print(f"API error: {e}")

        return request.render("silver_price.page_template", {
            'sections': sections,
            'last_update': last_update,
            'vat_note': vat_note,
            'hotline': hotline
        })
    
    def data_and_meta_processing(data):
        # Tách phần cuối của API (3 dòng meta)
        if len(data) >= 3:
            meta = data[-3:]
            data = data[:-3]  # bỏ 3 dòng cuối khỏi phần sản phẩm

            # Dòng thời gian
            if len(meta[0]) >= 3 and meta[0][2]:
                last_update = meta[0][2]
            # Dòng ghi chú thuế
            if len(meta[1]) >= 1:
                vat_note = meta[1][0]
            # Dòng hotline
            if len(meta[2]) >= 1:
                hotline = meta[2][0]
        return data
