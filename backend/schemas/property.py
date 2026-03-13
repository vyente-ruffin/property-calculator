from __future__ import annotations

from pydantic import BaseModel


class PropertyData(BaseModel):
    Price: str | None = None
    Address: str | None = None
    City: str | None = None
    Cap_Rate: str | None = None
    Date_On_Market: str | None = None
    Monthly_Rental_Income_Projected: str | None = None
    Monthly_Rental_Income_Actual: str | None = None
    Annual_Rent_Income_Projected: str | None = None
    Annual_Rent_Income_Actual: str | None = None
    NOI: str | None = None
    Lot_building_size: str | None = None
    Total_Units: int | None = None
    Unit_Mix_Summary: str | None = None
    Link: str | None = None
    Description: str | None = None
    Image_URL: str | None = None

    def to_display_dict(self) -> dict:
        """Return dict with user-friendly keys matching the original schema."""
        return {
            "Price": self.Price,
            "Address": self.Address,
            "City": self.City,
            "Cap Rate": self.Cap_Rate,
            "Date On Market": self.Date_On_Market,
            "Monthly Rental Income (Projected)": self.Monthly_Rental_Income_Projected,
            "Monthly Rental Income (Actual)": self.Monthly_Rental_Income_Actual,
            "Annual Rent Income (Projected)": self.Annual_Rent_Income_Projected,
            "Annual Rent Income (Actual)": self.Annual_Rent_Income_Actual,
            "NOI": self.NOI,
            "Lot / building size": self.Lot_building_size,
            "Total Units": self.Total_Units,
            "Unit Mix Summary": self.Unit_Mix_Summary,
            "Link": self.Link,
            "Description": self.Description,
            "Image URL": self.Image_URL,
        }

    @classmethod
    def from_display_dict(cls, d: dict) -> PropertyData:
        """Create from dict with user-friendly keys."""
        return cls(
            Price=d.get("Price"),
            Address=d.get("Address"),
            City=d.get("City"),
            Cap_Rate=d.get("Cap Rate"),
            Date_On_Market=d.get("Date On Market"),
            Monthly_Rental_Income_Projected=d.get("Monthly Rental Income (Projected)"),
            Monthly_Rental_Income_Actual=d.get("Monthly Rental Income (Actual)"),
            Annual_Rent_Income_Projected=d.get("Annual Rent Income (Projected)"),
            Annual_Rent_Income_Actual=d.get("Annual Rent Income (Actual)"),
            NOI=d.get("NOI"),
            Lot_building_size=d.get("Lot / building size"),
            Total_Units=d.get("Total Units"),
            Unit_Mix_Summary=d.get("Unit Mix Summary"),
            Link=d.get("Link"),
            Description=d.get("Description"),
            Image_URL=d.get("Image URL"),
        )


# JSON schema for Azure OpenAI structured outputs (strict mode)
PROPERTY_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "Price": {"type": ["string", "null"]},
        "Address": {"type": ["string", "null"]},
        "City": {"type": ["string", "null"]},
        "Cap Rate": {"type": ["string", "null"]},
        "Date On Market": {"type": ["string", "null"]},
        "Monthly Rental Income (Projected)": {"type": ["string", "null"]},
        "Monthly Rental Income (Actual)": {"type": ["string", "null"]},
        "Annual Rent Income (Projected)": {"type": ["string", "null"]},
        "Annual Rent Income (Actual)": {"type": ["string", "null"]},
        "NOI": {"type": ["string", "null"]},
        "Lot / building size": {"type": ["string", "null"]},
        "Total Units": {"type": ["integer", "null"]},
        "Unit Mix Summary": {"type": ["string", "null"]},
        "Link": {"type": ["string", "null"]},
        "Description": {"type": ["string", "null"]},
        "Image URL": {"type": ["string", "null"]},
    },
    "required": [
        "Price",
        "Address",
        "City",
        "Cap Rate",
        "Date On Market",
        "Monthly Rental Income (Projected)",
        "Monthly Rental Income (Actual)",
        "Annual Rent Income (Projected)",
        "Annual Rent Income (Actual)",
        "NOI",
        "Lot / building size",
        "Total Units",
        "Unit Mix Summary",
        "Link",
        "Description",
        "Image URL",
    ],
    "additionalProperties": False,
}
