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
        "version":1,
        "kind":"harness-human-projection-ir",
        "manifest_digest":plan["manifest_digest"],
        "documents":[
            {
                "id":doc["id"],
                "sections":[
                    {
                        "id":section["id"],
                        "claims":[
                            {
                                "text":f"Projection validation claim for {section['title']}.",
                                "sources":[section["sources"][0]],
                            }
                        ],
                    }
                    for section in doc["sections"]
                ],
            }
            for doc in plan["documents"]
        ],
    }

def validate_consumer(graph,model,consumer,recipe_path):
    recipe=load(recipe_path)
    manifest=compile_manifest(
        graph,model,consumer,
        harness_version="human-projection-v1-current-main",
        project_revision="nutrition-current-main",
        recipe_id=recipe["id"],
        source_root=ROOT,
    )
    assert manifest["target"]["status"]=="COMPLETE", manifest["target"]
    assert manifest["unresolved"]==[], manifest["unresolved"]
    plan=validate_recipe(recipe,manifest)
    ir=synthetic_ir(plan)
    with tempfile.TemporaryDirectory() as temp:
        root=Path(temp)/consumer.lower()
        result=materialize_package(manifest,plan,ir,root,mode="REVIEW")
        assert result["documents"]
        assert (root/"manifest.yaml").is_file()
    return manifest,plan

def main():
    graph=load(".harness/engineering-graph.yaml")
    model=load(".harness/graph.yaml")

    backend,_=validate_consumer(
        graph,model,"IMPLEMENTATION",
        "docs/research/human-projection-v1/backend.yaml",
    )
    frontend,frontend_plan=validate_consumer(
        graph,model,"FRONTEND-IMPLEMENTATION",
        "docs/research/human-projection-v1/frontend.yaml",
    )

    frontend_sources={row["artifact"] for row in frontend["sources"]}
    for required in (
        "FRONTEND-HUMAN-INTERFACE",
        "FRONTEND-PRESENTATION-SYSTEM",
        "FRONTEND-SCREEN-VIEW-DESIGN",
        "FRONTEND-ARCHITECTURE",
        "FRONTEND-COMPONENT-DESIGN",
        "FRONTEND-VERIFICATION-DESIGN",
        "FRONTEND-TEST-DESIGN",
        "FRONTEND-IMPLEMENTATION-DESIGN",
    ):
        assert required in frontend_sources, required

    section=next(
        section
        for doc in frontend_plan["documents"]
        for section in doc["sections"]
        if section["id"]=="screen-view-design"
    )
    assert section["sources"]==["FRONTEND-SCREEN-VIEW-DESIGN"]

    assert len(backend["sources"])>10
    assert len(frontend["sources"])>10
    print("Nutrition current-main Human Projection v1 PASS")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
