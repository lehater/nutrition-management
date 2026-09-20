#!/usr/bin/env python3
from __future__ import annotations
import os, sys, tempfile
from pathlib import Path
import yaml

ROOT=Path(__file__).resolve().parents[1]
HARNESS=Path(os.environ.get("HUMAN_PROJECTION_HARNESS", ROOT/".human-projection-harness"))
sys.path.insert(0,str(HARNESS))
from human_projection import compile_manifest, materialize_package, validate_recipe

def load(path):
    return yaml.safe_load((ROOT/path).read_text(encoding="utf-8"))

def synthetic_ir(plan):
    return {
        "version": 1,
        "kind": "harness-human-projection-ir",
        "manifest_digest": plan["manifest_digest"],
        "documents": [
            {
                "id": document["id"],
                "sections": [
                    {
                        "id": section["id"],
                        "claims": [
                            {
                                "text": f"Research projection for {section['title']}.",
                                "sources": [section["sources"][0]],
                            }
                        ],
                    }
                    for section in document["sections"]
                ],
            }
            for document in plan["documents"]
        ],
    }


def main():
    graph=load(".harness/engineering-graph.yaml")
    model=load(".harness/graph.yaml")

    backend_manifest=compile_manifest(
        graph,
        model,
        "IMPLEMENTATION",
        harness_version="research-prototype",
        project_revision="nutrition-research",
        recipe_id="nutrition-backend-human-docs",
        source_root=ROOT,
        extra_capabilities=[
            "nutrition-management.food-knowledge.nutrient-evidence-semantics"
        ],
    )
    assert backend_manifest["target"]["status"]=="COMPLETE", backend_manifest["target"]
    backend_plan=validate_recipe(load("docs/research/human-projection/backend.yaml"),backend_manifest)
    assert [d["id"] for d in backend_plan["documents"]]==["overview","domain-and-data","implementation-guide","verification-and-readiness"]

    frontend_manifest=compile_manifest(graph,model,"FRONTEND-IMPLEMENTATION",harness_version="research-prototype",project_revision="nutrition-research",recipe_id="nutrition-frontend-human-docs",source_root=ROOT)
    assert frontend_manifest["target"]["status"]=="COMPLETE", frontend_manifest["target"]
    frontend_plan=validate_recipe(load("docs/research/human-projection/frontend.yaml"),frontend_manifest)
    assert [d["id"] for d in frontend_plan["documents"]]==["frontend-guide"]

    backend_ir=synthetic_ir(backend_plan)
    frontend_ir=synthetic_ir(frontend_plan)

    with tempfile.TemporaryDirectory() as temp_dir:
        review=Path(temp_dir)/"review"
        result=materialize_package(
            backend_manifest,
            backend_plan,
            backend_ir,
            review,
            mode="REVIEW",
        )
        assert result["documents"]==[
            "domain-and-data.md",
            "implementation-guide.md",
            "overview.md",
            "verification-and-readiness.md",
        ], result

        handoff=Path(temp_dir)/"handoff"
        handoff_result=materialize_package(
            backend_manifest,
            backend_plan,
            backend_ir,
            handoff,
            mode="HANDOFF",
            source_root=ROOT,
        )
        assert len(handoff_result["sources"])==len(backend_manifest["sources"])
        assert (handoff/"sources/docs/requirements/product-requirements.md").is_file()

        frontend_review=Path(temp_dir)/"frontend-review"
        frontend_result=materialize_package(
            frontend_manifest,
            frontend_plan,
            frontend_ir,
            frontend_review,
            mode="REVIEW",
        )
        assert frontend_result["documents"]==["frontend-guide.md"]

    # Existing human docs are the quality/IA benchmark, not semantic inputs.
    for name in ("overview.md","domain-and-data.md","implementation-guide.md","verification-and-readiness.md","frontend-guide.md"):
        assert (ROOT/"docs/generated"/name).is_file(), name

    print("Nutrition human projection research PASS")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
