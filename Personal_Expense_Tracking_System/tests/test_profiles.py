import unittest

from tests.base import AppTestCase


class ProfileTests(AppTestCase):
    def setUp(self):
        super().setUp()
        self.food = self.make_category("Food")
        self.household = self.repo.list_profiles()[0]["id"]

    def add_profile(self, name):
        response = self.client.post("/people", data={"name": name})
        self.assertEqual(response.status_code, 302)
        return next(p["id"] for p in self.repo.list_profiles() if p["name"] == name)

    def test_add_and_list_profiles(self):
        ari = self.add_profile("Ari")
        page = self.client.get("/people")
        self.assertIn(b"Ari", page.data)
        self.assertEqual(self.repo.get_profile(ari)["name"], "Ari")

    def test_profile_names_are_required_and_unique(self):
        self.assertEqual(self.client.post("/people", data={"name": "  "}).status_code, 400)
        self.client.post("/people", data={"name": "Ari"})
        response = self.client.post("/people", data={"name": " ari "})
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"already exists", response.data)

    def test_expense_requires_a_valid_profile(self):
        response = self.client.post(
            "/expenses/add", data=self.form(self.food, profile_id="unknown"))
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Please choose a valid person.", response.data)
        self.assertEqual(self.repo.list_expenses(), [])

    def test_expenses_are_saved_filtered_and_exported_by_profile(self):
        ari = self.add_profile("Ari")
        self.make_expense(self.food, "Household tea", "10.00", profile_id=self.household)
        self.make_expense(self.food, "Ari lunch", "25.50", profile_id=ari)

        rows = self.repo.list_expenses({"profile_id": ari})
        self.assertEqual([row["title"] for row in rows], ["Ari lunch"])
        self.assertEqual(rows[0]["profile_name"], "Ari")

        page = self.client.get("/expenses?person=%d" % ari)
        self.assertIn(b"Ari lunch", page.data)
        self.assertNotIn(b"Household tea", page.data)

        dashboard = self.client.get("/?person=%d" % ari)
        self.assertIn(b"Rs.25.50", dashboard.data)
        self.assertIn(b'"total": 25.5', dashboard.data)

        report = self.client.get("/reports?month=2026-09&person=%d" % ari)
        self.assertIn(b"Rs.25.50", report.data)
        self.assertIn(
            ("/export.csv?start=2026-09-01&amp;end=2026-09-30&amp;person=%d" % ari).encode(),
            report.data)

        export = self.client.get("/export.csv?person=%d" % ari)
        self.assertIn(b"Ari lunch", export.data)
        self.assertNotIn(b"Household tea", export.data)

    def test_add_expense_prefills_selected_profile(self):
        ari = self.add_profile("Ari")
        page = self.client.get("/expenses/add?person=%d" % ari)
        self.assertIn(('value="%d" selected' % ari).encode(), page.data)

    def test_expense_can_be_reassigned_to_another_profile(self):
        ari = self.add_profile("Ari")
        expense_id = self.make_expense(self.food, "Shared bill")
        response = self.client.post(
            "/expenses/%d/edit" % expense_id,
            data=self.form(self.food, profile_id=str(ari)))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.repo.get_expense(expense_id)["profile_id"], ari)


if __name__ == "__main__":
    unittest.main()
