from vajra.recommender.engine import recommend_distros


def test_incompatible_architecture_is_filtered():
    hardware = {
        "architecture": "arm64",
        "ram_gb": 8,
        "physical_cores": 4,
        "firmware": "UEFI",
    }
    distros = [{
        "id": "test",
        "name": "Test Linux",
        "minimum_ram_gb": 2,
        "recommended_ram_gb": 4,
        "minimum_cores": 2,
        "architectures": ["x86_64"],
        "categories": [],
        "difficulty": "beginner",
        "official_download_page": "https://example.invalid",
        "supports_uefi": True,
        "supports_legacy_bios": True,
    }]
    assert recommend_distros(hardware, distros) == []
