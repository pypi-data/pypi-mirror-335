import pytest
from pypal.generator import generate_name, generate_address, generate_phone_number, generate_profile

HUMAN_FIRST = ["Alice", "Bob", "Charlie", "Diana", "Ethan", "Fiona", "George", "Hannah", "Isaac", "Julia"]
HUMAN_LAST= ["Smith", "Johnson", "Brown", "Taylor", "Anderson", "Clark", "Lewis", "Walker", "Young", "Hall"]
FANTASY_NAMES = ["Zorblax", "Elandra", "Thrain", "Myrrha", "Drakar", "Lyssara", "Volgrim", "Zenthra", "Kaelith", "Orvax"]

# Test generate_name function with human type
# Test if the generate name function is good with its iteration of generating list of human names (last + first name)
def test_generate_name_human_multiple():
    result = generate_name(type="human", length=3)
    assert isinstance(result, list)
    assert len(result) == 3  
    assert all(isinstance(name, str) and " " in name for name in result)  # All should be valid names

    # Ensure the expected format with valid first and last for all the names generated
    for name in result:
        first, last = name.split(" ")
        assert first in HUMAN_FIRST
        assert last in HUMAN_LAST

# Test if the generate name function can properly generate one human name
def test_generate_name_human_single():
    result = generate_name(type="human", length=1)
    assert isinstance(result, list)
    assert len(result) == 1  
    assert " " in result[0]  # Ensure first and last name exist

    # Ensure the expected format with valid first and last
    first, last = result[0].split(" ")
    assert first in HUMAN_FIRST
    assert last in HUMAN_LAST

# Test generate_name function with fantasy type
# Test if the generate name function is good with its iteration of generating list of fantasy names
def test_generate_name_fantasy_multiple():
    result = generate_name(type="fantasy", length=3)
    assert isinstance(result, list)
    assert len(result) == 3 
    assert all(isinstance(name, str) and " " not in name for name in result)  # Fantasy names should contain no space
    # Ensure each name is valid fantasy names
    for name in result:
        assert name in FANTASY_NAMES

# Test if the generate name function can properly generate one fantasy name
def test_generate_name_fantasy_single():
    result = generate_name(type="fantasy", length=1)
    assert isinstance(result, list)
    assert len(result) == 1  
    assert " " not in result[0]  # Ensure no space
    # Ensure valid fantasy name
    assert result[0] in FANTASY_NAMES

# Test if the generate name function can handle empty cases
def test_generate_name_human_zero():
    result = generate_name(type="human", length=0)
    assert isinstance(result, list)
    assert len(result) == 0  # Should return an empty list

    result = generate_name(type="fantasy", length=0)
    assert isinstance(result, list)
    assert len(result) == 0  # Should return an empty list

# Test function does not silently return empty names
def test_generate_name_not_empty():
    result = generate_name(type="human", length=2)
    assert all(name.strip() != "" for name in result)  

    result = generate_name(type="fantasy", length=2)
    assert all(name.strip() != "" for name in result)

# Edge case: Invalid type input, we want the user to choose from human or fantasy
# Representative invalid types
@pytest.mark.parametrize("invalid_type", ["alien", "humen", "fantacy", "unknown", "HUMAN", "FANTASY", 123, True, False, None])
def test_generate_name_invalid_type(invalid_type):
    with pytest.raises(ValueError):
        generate_name(type=invalid_type, length=2) 


STREETS = ["123 Maple St", "456 Oak Ave", "789 Pine Rd", "101 Elm St", "202 Birch Blvd", "303 Cedar Ln", "404 Spruce Ct", "505 Walnut Way"]
CITIES = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", "San Antonio", "San Diego"]
US_POSTCODES = ["10001", "90001", "60601", "77001", "85001", "19101", "78201", "92101"]
UK_POSTCODES = ["EC1A 1BB", "W1A 0AX", "M1 1AE", "B33 8TH", "CR2 6XH", "DN55 1PT", "E1 6AN", "N1 9GU"]

# Test if the generate address function generate correct address for country US
# Test the correctness of generating short address
def test_generate_address_us_short():
    result = generate_address(country = "US", format = "short")
    assert isinstance(result, str)
    
    # Check individual components
    parts = result.split(", ")
    assert len(parts) == 2 
    street, city = parts
    # must have one valid street, one valid city
    assert street in STREETS
    assert city in CITIES
    assert not any(postcode in result for postcode in US_POSTCODES) # no postal code in short
    assert "USA" not in result # no country in short

# Test the correctness of generating long address
def test_generate_address_us_long():
    result = generate_address(country = "US", format = "long")
    assert isinstance(result, str)

    # Check individual components
    parts = result.split(", ")
    assert len(parts) == 4
    street, city, postcode, country = parts
    # must have one valid street, city, postcode, country
    assert street in STREETS
    assert city in CITIES
    assert any(postcode in result for postcode in US_POSTCODES) # contains valid us postal code
    assert "USA" in result

# Test if the generate address function generate correct address for country uk
# Test the correctness of generating short address
def test_generate_address_uk_short():
    result = generate_address(country = "UK", format = "short")
    assert isinstance(result, str)

    # Check individual components
    parts = result.split(", ")
    assert len(parts) == 2
    street, city = parts
    # must have one valid street, city
    assert street in STREETS
    assert city in CITIES
    assert not any(postcode in result for postcode in UK_POSTCODES) # no postal code in short
    assert "UK" not in result # no country in short

# Test the correctness of generating long address
def test_generate_address_uk_long():
    result = generate_address(country = "UK", format = "long")
    assert isinstance(result, str)

    # Check individual components
    parts = result.split(", ")
    assert len(parts) == 4
    street, city, uk_postcode, country = parts
    # must have one valid street, city, postcode, country
    assert street in STREETS
    assert city in CITIES
    assert any(postcode in result for postcode in UK_POSTCODES) # contains valid us postal code
    assert "UK" in result

# Test function does not silently return empty string
def test_generate_address_not_empty():
    result = generate_address(country="US", format="short")
    assert result.strip() != ""

# Edge case: Test invalid country inputs
# Representative invalid countries
@pytest.mark.parametrize("invalid_country", ["France", "Germany", "Us", "us", "uS", "Uk", "uk", "uK", "", 123, True, False, None])
def test_generate_address_invalid_country(invalid_country):
    with pytest.raises(ValueError):
        generate_address(country=invalid_country, format="short")

# Edge case: Test invalid format inputs
# Representative invalid format
@pytest.mark.parametrize("invalid_format", ["SHORT", "LONG", "medium", "", 123, True, False, None])
def test_generate_address_invalid_format(invalid_format):
    with pytest.raises(ValueError):
        generate_address(country="US", format=invalid_format)


# Test if the domestic phone numbers generated are valid
def test_generate_phone_number_domestic():
    result = generate_phone_number(style="domestic")
    assert isinstance(result, str)  

    # Check format
    assert len(result) == 14  # Expected format: "(xxx) xxx-xxxx"
    assert result[0] == "("  
    assert result[4] == ")"  
    assert result[5] == " "  
    assert result[9] == "-"  

    # Extract things in between, make sure there are 10 numbers
    numeric_parts = result.replace("(", "").replace(")", "").replace(" ", "").replace("-", "")
    assert numeric_parts.isdigit()  
    assert len(numeric_parts) == 10  

# Test if the international phone numbers generated are valid
def test_generated_phone_number_international():
    result = generate_phone_number(style="international")
    assert isinstance(result, str)

    # Check format
    assert len(result) == 15 # Expected format: "+1-xxx-xxx-xxxx"
    assert result[0] == "+"
    assert result[1] == "1"
    assert result[2] == "-"
    assert result[6] == "-"
    assert result[10] == "-"

    # Extract things in between, make sure there are 10 numbers
    numeric_parts = result.replace("+1-", "").replace("-", "")
    assert numeric_parts.isdigit()  
    assert len(numeric_parts) == 10 

# Test function does not return an empty string
def test_generate_phone_number_not_empty():
    result = generate_phone_number(style="domestic")
    assert result.strip() != ""  

    result = generate_phone_number(style="international")
    assert result.strip() != ""  

# Edge case: Test invalid style inputs
# Representative invalid style
@pytest.mark.parametrize("invalid_style", ["Domestic", "INTERNATIONAL", "mobiile", "random", "", 123, True, False, None])
def test_generate_phone_number_case_sensitive_fail(invalid_style):
    with pytest.raises(ValueError):
        generate_phone_number(style=invalid_style)


# Test of the generate_profile function can generate valid profiles
# Test the correctness of generating prfile with both email and phone numbers included
def test_generate_profile_full():
    profile = generate_profile(include_email=True, include_phone=True)
    assert isinstance(profile, dict)
    assert "name" in profile
    assert "address" in profile
    assert "email" in profile
    assert "phone" in profile

    # Validate individual components
    assert isinstance(profile["name"], str) and " " in profile["name"]  
    assert isinstance(profile["address"], str) and profile["address"].strip() != ""  
    assert isinstance(profile["email"], str) and "@" in profile["email"] and profile["email"].endswith("@example.com")
    assert isinstance(profile["phone"], str) and profile["phone"].strip() != ""

# Test the correctness of generating profile with only email
def test_generate_profile_email():
    profile = generate_profile(include_email=True, include_phone=False)
    assert isinstance(profile, dict)
    assert "name" in profile
    assert "address" in profile
    assert "email" in profile
    assert "phone" not in profile

    # Validate individual components
    assert isinstance(profile["name"], str) and " " in profile["name"]
    assert isinstance(profile["address"], str) and profile["address"].strip() != ""
    assert isinstance(profile["email"], str) and "@" in profile["email"] and profile["email"].endswith("@example.com")
    
# Test the correctness of generating profile with only phone
def test_generate_profile_phone():
    profile = generate_profile(include_email=False, include_phone=True)
    assert "name" in profile
    assert "address" in profile
    assert "email" not in profile
    assert "phone" in profile

    # Validate individual components
    assert isinstance(profile["name"], str) and " " in profile["name"]
    assert isinstance(profile["address"], str) and profile["address"].strip() != ""
    assert isinstance(profile["phone"], str) and profile["phone"].strip() != ""

# Test the correctness of generating profile with only name and address
def test_generate_profile_basic():
    profile = generate_profile(include_email=False, include_phone=False)
    assert isinstance(profile, dict)
    assert "name" in profile
    assert "address" in profile
    assert "email" not in profile  
    assert "phone" not in profile 

    # Validate individual components
    assert isinstance(profile["name"], str) and " " in profile["name"]
    assert isinstance(profile["address"], str) and profile["address"].strip() != ""

# Test creating valid email with name
def test_generate_profile_email_format():
    profile = generate_profile(include_email=True, include_phone=False)
    first_name = profile["name"].split()[0].lower()
    expected_email = f"{first_name}@example.com"

    assert profile["email"] == expected_email

# Test profile contains only expected info
def test_generate_profile_contents():
    profile = generate_profile(include_email=True, include_phone=True)
    assert set(profile.keys()) == {"name", "address", "email", "phone"}  

    profile = generate_profile(include_email=True, include_phone=False)
    assert set(profile.keys()) == {"name", "address", "email"}

    profile = generate_profile(include_email=False, include_phone=True)
    assert set(profile.keys()) == {"name", "address", "phone"}

    profile = generate_profile(include_email=False, include_phone=False)
    assert set(profile.keys()) == {"name", "address"}

# Test profile info order
def test_generate_profile_order():
    profile = generate_profile(include_email=True, include_phone=True)
    expected_order = ["name", "address", "email", "phone"]
    assert list(profile.keys()) == expected_order  

    profile = generate_profile(include_email=False, include_phone=True)
    expected_order = ["name", "address", "phone"]
    assert list(profile.keys()) == expected_order  

    profile = generate_profile(include_email=True, include_phone=False)
    expected_order = ["name", "address", "email"]
    assert list(profile.keys()) == expected_order  

    profile = generate_profile(include_email=False, include_phone=False)
    expected_order = ["name", "address"]
    assert list(profile.keys()) == expected_order

# Test function never returns empty strings silently
def test_generate_profile_not_empty():
    profile = generate_profile(include_email=True, include_phone=True)

    assert profile["name"].strip() != ""  
    assert profile["address"].strip() != ""  
    assert profile["email"].strip() != ""  
    assert profile["phone"].strip() != ""  