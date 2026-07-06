def _architecture_matches(machine_arch, supported):
    aliases = {
        "x86_64": {"x86_64", "amd64"},
        "amd64": {"x86_64", "amd64"},
    }
    accepted = aliases.get(machine_arch, {machine_arch})
    return bool(accepted.intersection(set(supported)))


def recommend_distros(hardware, distros, preferences=None):
    preferences = preferences or {}
    results = []

    for distro in distros:
        reasons = []
        score = 50

        if not _architecture_matches(
            hardware["architecture"], distro["architectures"]
        ):
            continue

        ram = hardware["ram_gb"]
        if ram < distro["minimum_ram_gb"]:
            continue
        elif ram >= distro["recommended_ram_gb"]:
            score += 20
            reasons.append("Your RAM meets the recommended level.")
        else:
            score += 10
            reasons.append("Your RAM meets the minimum requirement.")

        cores = hardware["physical_cores"]
        if cores >= distro["minimum_cores"]:
            score += 10
            reasons.append("Your CPU core count is suitable.")

        firmware = hardware["firmware"]
        if firmware == "UEFI" and distro["supports_uefi"]:
            score += 5
            reasons.append("UEFI boot is supported.")
        elif firmware == "Legacy BIOS" and distro["supports_legacy_bios"]:
            score += 5
            reasons.append("Legacy BIOS boot is supported.")

        purpose = preferences.get("purpose")
        if purpose and purpose in distro["categories"]:
            score += 10
            reasons.append(f"Good match for your {purpose.replace('_', ' ')} use case.")

        experience = preferences.get("experience")
        if experience and experience == distro["difficulty"]:
            score += 5
            reasons.append(f"Matches your {experience} experience level.")

        if ram <= 4 and "old_pc" in distro["categories"]:
            score += 10
            reasons.append("Optimized score for lower-memory hardware.")

        results.append({
            "id": distro["id"],
            "name": distro["name"],
            "score": min(score, 100),
            "reasons": reasons,
            "official_download_page": distro["official_download_page"],
        })

    return sorted(results, key=lambda item: item["score"], reverse=True)
