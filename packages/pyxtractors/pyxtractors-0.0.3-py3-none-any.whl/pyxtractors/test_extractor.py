import pytest

from .extractor import *



@pytest.fixture
def data() -> Dict[str, Any]:
	return {
		"first-name": "John",
		"last-name": "Doe",
		"age": 32,
		"address": {
			"country": "UK",
			"street": "Baker st."
		},
		"married": True
	}



def testExtractByKey(data: Dict[str, Any]):
	extractor = KeyExtractor("last-name")
	assert "Doe" == extractor(data)



def testExtractWithDefault(data: Dict[str, Any]):
	basicExtractor = KeyExtractor("middle-name")
	extractor = ExtractorWithErrDefault(basicExtractor, "UNKNOWN")
	assert "UNKNOWN" == extractor(data)



def testExtractTransformed(data: Dict[str, Any]):
	def transformer(value: int):
		return "even" if value % 2 == 0 else "odd"

	basicExtractor = KeyExtractor("age")
	extractor = TransformExtractor(basicExtractor, transformer)
	assert "even" == extractor(data)



def testMassExtraction(data: Dict[str, Any]):
	countryNames = {
		"FR": "France",
		"US": "United States",
		"UK": "United Kingdom"
	}

	extractor = MassExtractor(
		name = KeyExtractor("first-name"),
		surname = KeyExtractor("last-name"),
		old = FuncExtractor(lambda age: age >= 60),
		country = ExtractorChain(
			KeyExtractor("address"),
			FuncExtractor(lambda country: countryNames[country])
		)
	)

	expected: Dict[str, Any] = {
		"name": "John",
		"surname": "Doe",
		"old": False,
		"country": "United Kingdom"
	}

	extracted = extractor(data)
	assert expected == extracted
