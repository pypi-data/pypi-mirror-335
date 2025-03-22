from avatar_yaml.models.config import Config
from tests.conftest import from_pretty_yaml


def test_config_standard():
    c=Config(seed=1,set_name='set_name')
    c.create_volume('test_metadata','http://example.com')
    c.create_results_volume('volume_results','http://example.com')
    c.create_results(path='volume_results')
    c.create_table(table_name='example_data',
                   original_volume='test_metadata',
                   original_file='iris.csv',
                   primary_key='id',
                   foreign_keys=['id_1, id_2'],)
    c.create_parameters(table_name='example_data',
                        k=3,
                        )

    yaml=c.get_yaml()
    print(yaml)
    expected_yaml = from_pretty_yaml("""
kind: AvatarVolume
metadata:
  name: test_metadata
spec:
  url: http://example.com

---
kind: AvatarVolume
metadata:
  name: volume_results
spec:
  url: http://example.com

---
kind: AvatarSchema
metadata:
  name: set_name
spec:
  tables:
  - name: example_data
    data:
      volume: test_metadata
      file: iris.csv
    individual_level: false
    columns:
    - field: id
      primary_key: true
    - field: id_1, id_2
      identifier: true

---
kind: AvatarSchema
metadata:
  name: set_name_avatarized
spec:
  tables: []
  schema_ref: set_name

---
kind: AvatarParameters
metadata:
  name: avatarization
spec:
  schema: set_name
  avatarization:
    example_data:
      k: 3
  results:
    volume: volume_results
    path: volume_results
  seed: 1

---
kind: AvatarPrivacyMetricsParameters
metadata:
  name: privacy
spec:
  schema: set_name_avatarized
  avatarization_ref: avatarization
  results:
    volume: volume_results
    path: volume_results
  seed: 1

---
kind: AvatarSignalMetricsParameters
metadata:
  name: signal
spec:
  schema: set_name_avatarized
  avatarization_ref: avatarization
  results:
    volume: volume_results
    path: volume_results
  seed: 1

---
kind: AvatarReportParameters
metadata:
  name: report
spec:
  report_type: basic
  results:
    volume: volume_results
    path: volume_results
""")
    assert expected_yaml==yaml


def test_config_multitable():
    c=Config(seed=1,set_name='set_name')
    c.create_volume('fixtures','{root:uri}/../')
    c.create_results_volume('local-temp-results','file:///tmp/avatar')
    c.create_results(path='volume_results')
    c.create_table(table_name='patient',
                   original_volume='fixtures',
                   original_file='multitable/table_patient.csv',
                   avatar_volume='fixtures',
                   avatar_file='multitable/table_patient_avatar.csv',
                   primary_key='patient_id',
                   types={'patient_id': 'category', 'age': 'int'},
                   individual_level=True)

    c.create_table(table_name='doctor',
                   original_volume='fixtures',
                   original_file='multitable/table_doctor.csv',
                   avatar_volume='fixtures',
                   avatar_file='multitable/table_doctor_avatar.csv',
                   primary_key='id',
                   types={'id': 'category', 'job': 'category'},
                   individual_level=True)

    c.create_table(table_name='visit',
                   original_volume='fixtures',
                   original_file='multitable/table_visit.csv',
                   avatar_volume='fixtures',
                   avatar_file='multitable/table_visit_avatar.csv',
                   primary_key='visit_id',
                   foreign_keys=['patient_id', 'doctor_id'],
                   types={'visit_id': 'category', 'doctor_id': 'category', 'patient_id': 'category', 'weight': 'int'},
                   individual_level=False)

    c.create_link('doctor','visit','id','doctor_id', 'sensitive_original_order_assignment')
    c.create_link('patient','visit','patient_id','patient_id', 'sensitive_original_order_assignment')


    c.create_parameters(table_name='patient',
                        k=3,
                        )
    c.create_parameters(table_name='doctor',
                        k=3,
                        use_categorical_reduction=True,
                        )
    c.create_parameters(table_name='visit',
                        k=3,
                        )
    c.create_report('privacy_report')

    yaml=c.get_yaml()
    print(yaml)
    expected_yaml = from_pretty_yaml("""
kind: AvatarVolume
metadata:
  name: fixtures
spec:
  url: '{root:uri}/../'

---
kind: AvatarVolume
metadata:
  name: local-temp-results
spec:
  url: file:///tmp/avatar

---
kind: AvatarSchema
metadata:
  name: set_name
spec:
  tables:
  - name: patient
    data:
      volume: fixtures
      file: multitable/table_patient.csv
    individual_level: true
    columns:
    - field: patient_id
      type: category
      primary_key: true
    - field: age
      type: int
    links:
    - field: patient_id
      to:
        table: visit
        field: patient_id
      method: sensitive_original_order_assignment
  - name: doctor
    data:
      volume: fixtures
      file: multitable/table_doctor.csv
    individual_level: true
    columns:
    - field: id
      type: category
      primary_key: true
    - field: job
      type: category
    links:
    - field: id
      to:
        table: visit
        field: doctor_id
      method: sensitive_original_order_assignment
  - name: visit
    data:
      volume: fixtures
      file: multitable/table_visit.csv
    individual_level: false
    columns:
    - field: visit_id
      type: category
      primary_key: true
    - field: patient_id
      type: category
      identifier: true
    - field: doctor_id
      type: category
      identifier: true
    - field: weight
      type: int

---
kind: AvatarSchema
metadata:
  name: set_name_avatarized
spec:
  tables:
  - name: patient
    individual_level: false
    avatars_data:
      volume: fixtures
      file: multitable/table_patient_avatar.csv
  - name: doctor
    individual_level: false
    avatars_data:
      volume: fixtures
      file: multitable/table_doctor_avatar.csv
  - name: visit
    individual_level: false
    avatars_data:
      volume: fixtures
      file: multitable/table_visit_avatar.csv
  schema_ref: set_name

---
kind: AvatarParameters
metadata:
  name: avatarization
spec:
  schema: set_name
  avatarization:
    patient:
      k: 3
    doctor:
      k: 3
      use_categorical_reduction: true
    visit:
      k: 3
  results:
    volume: local-temp-results
    path: volume_results
  seed: 1

---
kind: AvatarPrivacyMetricsParameters
metadata:
  name: privacy
spec:
  schema: set_name_avatarized
  avatarization_ref: avatarization
  privacy_metrics:
    doctor:
      use_categorical_reduction: true
  results:
    volume: local-temp-results
    path: volume_results
  seed: 1

---
kind: AvatarSignalMetricsParameters
metadata:
  name: signal
spec:
  schema: set_name_avatarized
  avatarization_ref: avatarization
  signal_metrics:
    doctor:
      use_categorical_reduction: true
  results:
    volume: local-temp-results
    path: volume_results
  seed: 1

---
kind: AvatarReportParameters
metadata:
  name: privacy_report
spec:
  report_type: basic
  results:
    volume: local-temp-results
    path: volume_results
""")
    assert expected_yaml==yaml
