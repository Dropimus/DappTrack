import flet as ft

def main(page):
    choosen_date = {}
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    def handle_start_date_change(e: ft.ControlEvent):
        choosen_date['start_date'] = e.control.value.strftime('%Y-%m-%d %H:%M %p')
        start_date_text.value = f"Start Date: {choosen_date['start_date']}"
        page.update()

    def handle_end_date_change(e: ft.ControlEvent):
        choosen_date['end_date'] = e.control.value.strftime('%Y-%m-%d %H:%M %p')
        end_date_text.value = f"End Date: {choosen_date['end_date']}"
        page.update()

    cupertino_date_picker_start = ft.CupertinoDatePicker(
        date_picker_mode=ft.CupertinoDatePickerMode.DATE_AND_TIME,
        on_change=handle_start_date_change,
    )
    
    cupertino_date_picker_end = ft.CupertinoDatePicker(
        date_picker_mode=ft.CupertinoDatePickerMode.DATE_AND_TIME,
        on_change=handle_end_date_change,
    )

    # Text controls for displaying the selected start and end dates
    start_date_text = ft.Text(f"Start Date: {choosen_date.get('start_date', 'Not selected yet')}")
    end_date_text = ft.Text(f"End Date: {choosen_date.get('end_date', 'Not selected yet')}")

    page.add(
        start_date_text,  # Display start date
        end_date_text,  # Display end date
        ft.CupertinoFilledButton(
            "Select Start Date",
            on_click=lambda e: page.open(
                ft.CupertinoBottomSheet(
                    cupertino_date_picker_start,
                    height=216,
                    padding=ft.padding.only(top=6),
                )
            ),
        ),
        ft.CupertinoFilledButton(
            "Select End Date",
            on_click=lambda e: page.open(
                ft.CupertinoBottomSheet(
                    cupertino_date_picker_end,
                    height=216,
                    padding=ft.padding.only(top=6),
                )
            ),
        ),
    )

ft.app(main)
