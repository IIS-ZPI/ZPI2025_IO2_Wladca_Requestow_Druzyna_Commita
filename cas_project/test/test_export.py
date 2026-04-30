import pytest
import os
from export import export_to_csv

def test_export_to_csv(tmp_path):
    data = [{"Metric": "Rising", "Value": 5}, {"Metric": "Falling", "Value": 2}]
    
    # Use temporary path from pytest
    csv_file = tmp_path / "test_output.csv"
    
    export_to_csv(data, str(csv_file))
    
    assert os.path.exists(csv_file)
    with open(csv_file, 'r') as f:
         content = f.read()
         assert "Metric,Value" in content
         assert "Rising,5" in content
