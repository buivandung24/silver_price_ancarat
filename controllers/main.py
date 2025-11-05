from odoo import http
from odoo.http import request
import requests

class SilverPriceController(http.Controller):

    @http.route('/banggia', type='http', auth='public', website=True)
    def silver_price(self, **kw):
        api_url = "https://giabac.ancarat.com/api/price-data"
        sections = []
        current_section = None
        last_update = ""
        vat_note = ""
        hotline = ""

        try:
            response = requests.get(api_url, timeout=300)
            if response.status_code == 200:
                data = response.json()

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
