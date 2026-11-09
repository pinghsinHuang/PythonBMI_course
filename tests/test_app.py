import unittest

from app import app, bmi_guidance


class BmiAppTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_initial_page(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        page = response.get_data(as_text=True)
        self.assertIn("從 BMI 開始，<br><em>認識自己的身體。</em>", page)
        self.assertIn("計算你的 BMI", page)

    def test_calculation_and_advice(self):
        response = self.client.post("/", data={"height": "170", "weight": "65"})
        page = response.get_data(as_text=True)
        self.assertIn("22.5", page)
        self.assertIn("健康體位", page)
        self.assertIn("維持均衡飲食", page)

    def test_name_is_shown_before_personalized_advice(self):
        response = self.client.post(
            "/", data={"name": "小明", "height": "170", "weight": "65"}
        )
        page = response.get_data(as_text=True)

        self.assertIn('id="name" name="name"', page)
        self.assertIn('value="小明"', page)
        self.assertIn("<p>小明，維持均衡飲食", page)

    def test_blank_name_keeps_generic_advice(self):
        response = self.client.post(
            "/", data={"name": "   ", "height": "170", "weight": "65"}
        )
        page = response.get_data(as_text=True)

        self.assertIn("<p>維持均衡飲食", page)
        self.assertNotIn("<p>，維持均衡飲食", page)

    def test_name_is_escaped_in_personalized_advice(self):
        response = self.client.post(
            "/",
            data={
                "name": "<img src=x onerror=alert(1)>",
                "height": "170",
                "weight": "65",
            },
        )
        page = response.get_data(as_text=True)

        self.assertIn("&lt;img src=x onerror=alert(1)&gt;，", page)
        self.assertNotIn("<img src=x onerror=alert(1)>", page)

    def test_name_is_preserved_when_calculation_inputs_are_invalid(self):
        response = self.client.post(
            "/", data={"name": "小明", "height": "", "weight": "65"}
        )
        page = response.get_data(as_text=True)

        self.assertIn('id="name" name="name"', page)
        self.assertIn('value="小明"', page)
        self.assertIn('aria-invalid="true"', page)

    def test_bmi_gauge_displays_result_and_position(self):
        response = self.client.post("/", data={"height": "100", "weight": "22.5"})
        page = response.get_data(as_text=True)

        self.assertIn('style="--bmi-position: 56.25%"', page)
        self.assertIn('aria-label="BMI 區間刻度，目前為健康體位"', page)
        for category in ["體重過輕", "健康體位", "體重過重", "肥胖"]:
            with self.subTest(category=category):
                self.assertIn(category, page)

    def test_bmi_gauge_position_starts_at_zero(self):
        response = self.client.post("/", data={"height": "100", "weight": "0.04"})

        self.assertIn('style="--bmi-position: 0.0%"', response.get_data(as_text=True))

    def test_bmi_gauge_position_clamps_at_scale_maximum(self):
        response = self.client.post("/", data={"height": "100", "weight": "40"})

        self.assertIn('style="--bmi-position: 100.0%"', response.get_data(as_text=True))

    def test_bmi_gauge_position_clamps_above_scale_maximum(self):
        for weight in ["50", "1e308"]:
            with self.subTest(weight=weight):
                response = self.client.post("/", data={"height": "100", "weight": weight})
                page = response.get_data(as_text=True)

                self.assertIn('style="--bmi-position: 100.0%"', page)

    def test_taiwan_adult_thresholds(self):
        for bmi, category in [
            (18.4, "體重過輕"),
            (18.5, "健康體位"),
            (23.9, "健康體位"),
            (24.0, "體重過重"),
            (26.9, "體重過重"),
            (27.0, "肥胖"),
        ]:
            with self.subTest(bmi=bmi):
                self.assertEqual(bmi_guidance(bmi)["label"], category)

    def test_invalid_fields_do_not_produce_result(self):
        for height, weight in [("", "65"), ("0", "65"), ("abc", "65"), ("170", "-2"), ("inf", "65"), ("170", "nan"), ("1e-300", "65"), ("1e308", "65"), ("1", "1e308")]:
            with self.subTest(height=height, weight=weight):
                response = self.client.post("/", data={"height": height, "weight": weight})
                page = response.get_data(as_text=True)
                self.assertEqual(response.status_code, 200)
                self.assertIn('aria-invalid="true"', page)
                self.assertNotIn("YOUR RESULT", page)

    def test_input_is_escaped(self):
        response = self.client.post("/", data={"height": '<script>alert(1)</script>', "weight": "65"})
        page = response.get_data(as_text=True)
        self.assertNotIn("<script>", page)
        self.assertIn("請輸入大於 0", page)


if __name__ == "__main__":
    unittest.main()
