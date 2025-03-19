# These tests send real requests and should be used with the API in dev mode.
import os
import unittest

import requests
from dotenv import load_dotenv

from cortecs_py.client import Cortecs
from cortecs_py.schemas import InstanceArgs


class TestInstanceArgs(unittest.TestCase):
    def setUp(self) -> None:
        load_dotenv()
        self.client = Cortecs()

    def test_get_default_instance_args_with_model_id(self) -> None:
        instance_args = {
            "model_id": "Qwen--Qwen2-7B-Instruct",
        }
        default_instance_args = self.client._get_default_instance_args(instance_args)
        expected_default_instance_args = {
            "model_id": "Qwen--Qwen2-7B-Instruct",
            "hardware_type_id": "NVIDIA_L4_1",
            "context_length": 32000,
            "billing_interval": "per_minute",
            "num_workers": 1,
        }
        self.assertEqual(default_instance_args, InstanceArgs(**expected_default_instance_args))
        
    def test_get_default_instance_args_with_hardware_type(self) -> None:
        instance_args = {
            "model_id": "Qwen--Qwen2-7B-Instruct",
            "hardware_type_id": "NVIDIA_L4_2",
        }
        default_instance_args = self.client._get_default_instance_args(instance_args)
        expected_default_instance_args = {
            "model_id": "Qwen--Qwen2-7B-Instruct",
            "hardware_type_id": "NVIDIA_L4_2",
            "context_length": 32000,
            "billing_interval": "per_minute",
            "num_workers": 1,
        }
        self.assertEqual(default_instance_args, InstanceArgs(**expected_default_instance_args))
    
    def test_get_default_instance_args_with_context_length(self) -> None:
        instance_args = {
            "model_id": "Qwen--Qwen2-7B-Instruct",
            "context_length": 16000,
        }
        default_instance_args = self.client._get_default_instance_args(instance_args)
        expected_default_instance_args = {
            "model_id": "Qwen--Qwen2-7B-Instruct",
            "hardware_type_id": "NVIDIA_L4_1",
            "context_length": 16000,
            "billing_interval": "per_minute",
            "num_workers": 1,
        }
        self.assertEqual(default_instance_args, InstanceArgs(**expected_default_instance_args))
    
    def test_get_default_instance_args_with_billing_interval(self) -> None:
        instance_args = {
            "model_id": "Qwen--Qwen2-7B-Instruct",
            "billing_interval": "per_hour",
        }
        default_instance_args = self.client._get_default_instance_args(instance_args)
        expected_default_instance_args = {
            "model_id": "Qwen--Qwen2-7B-Instruct",
            "hardware_type_id": "NVIDIA_L4_1",
            "context_length": 32000,
            "billing_interval": "per_hour",
            "num_workers": 1,
        }
        self.assertEqual(default_instance_args, InstanceArgs(**expected_default_instance_args))
        
    def test_get_default_instance_args_with_num_workers(self) -> None:
        instance_args = {
            "model_id": "Qwen--Qwen2-7B-Instruct",
            "num_workers": "2",
        }
        default_instance_args = self.client._get_default_instance_args(instance_args)
        expected_default_instance_args = {
            "model_id": "Qwen--Qwen2-7B-Instruct",
            "hardware_type_id": "NVIDIA_L4_1",
            "context_length": 32000,
            "billing_interval": "per_minute",
            "num_workers": 2,
        }
        self.assertEqual(default_instance_args, InstanceArgs(**expected_default_instance_args))
    
    def test_get_default_instance_args_with_invalid_context_length_recommended_config(self) -> None:
        instance_args = {
            "model_id": "Qwen--Qwen2-7B-Instruct",
            "context_length": 64000,
        }
        with self.assertRaises(ValueError):
            self.client._get_default_instance_args(instance_args)

    def test_get_default_instance_args_with_invalid_context_length_set_config(self) -> None:
        instance_args = {
            "model_id": "Qwen--Qwen2-7B-Instruct",
            "hardware_type_id": "NVIDIA_L4_2",
            "context_length": 64000,
        }
        with self.assertRaises(ValueError):
            self.client._get_default_instance_args(instance_args)


class TestAuthentication(unittest.TestCase):
    def setUp(self) -> None:
        load_dotenv()
        self.client = Cortecs()

    def test_get_token(self) -> None:
        self.client._get_token()
        self.assertIsNotNone(self.client.token)

    def test_request_with_auth(self) -> None:
        self.client._get_token()
        response = self.client._request("GET", "/instances", auth_required=True)
        self.assertEqual(response.status_code, 200)

    def test_request_without_auth(self) -> None:
        with self.assertRaises(requests.exceptions.HTTPError):
            self.client._request("GET", "/instances", auth_required=False)


class TestInstanceManagement(unittest.TestCase):
    def setUp(self) -> None:
        load_dotenv()
        self.assertEqual(os.environ["CORTECS_API_BASE_URL"], "http://localhost:3000/api/v1")
        self.client = Cortecs()

    def tearDown(self) -> None:
        self.client.delete_all(force=True)

    def test_start_instance(self) -> None:
        instance = self.client.start("Qwen/Qwen2-7B-Instruct", poll=True)
        self.assertEqual(instance.instance_status.status, "running")

    def test_stop_instance(self) -> None:
        instance = self.client.start("Qwen/Qwen2-7B-Instruct", poll=True)
        instance = self.client.stop(instance.instance_id)
        self.assertEqual(instance.instance_status.status, "stopped")

    def test_restart_instance(self) -> None:
        instance = self.client.start("Qwen/Qwen2-7B-Instruct", poll=True)
        instance = self.client.stop(instance.instance_id)
        instance = self.client.restart(instance.instance_id, poll=True)
        self.assertEqual(instance.instance_status.status, "running")

    def test_ensure_instance_running(self) -> None:
        instance_1 = self.client.start("Qwen/Qwen2-7B-Instruct", poll=True)
        instance_2 = self.client.ensure_instance("Qwen/Qwen2-7B-Instruct", poll=True)
        self.assertEqual(instance_1.instance_id, instance_2.instance_id)
        
    def test_ensure_instance_num_workers(self) -> None:
        instance_1 = self.client.start("Qwen/Qwen2-7B-Instruct", poll=True)
        instance_2 = self.client.ensure_instance("Qwen/Qwen2-7B-Instruct", num_workers=2, poll=True)
        self.assertNotEqual(instance_1.instance_id, instance_2.instance_id)

    def test_ensure_instance_stopped(self) -> None:
        instance_1 = self.client.start("Qwen/Qwen2-7B-Instruct", poll=True)
        instance_1 = self.client.stop(instance_1.instance_id)
        instance_2 = self.client.ensure_instance("Qwen/Qwen2-7B-Instruct", poll=True)
        self.assertEqual(instance_1.instance_id, instance_2.instance_id)

    def test_ensure_instance_new(self) -> None:
        instance = self.client.ensure_instance("Qwen/Qwen2-7B-Instruct", poll=True)
        self.assertIsNotNone(instance.instance_id)

    def test_get_instance(self) -> None:
        instance_1 = self.client.start("Qwen/Qwen2-7B-Instruct", poll=True)
        instance_2 = self.client.get_instance(instance_1.instance_id)
        self.assertEqual(instance_1.instance_id, instance_2.instance_id)

    def test_get_all_instances(self) -> None:
        instances = self.client.get_all_instances()
        self.assertIsInstance(instances, list)

    def test_delete_instance(self) -> None:
        instance = self.client.start("Qwen/Qwen2-7B-Instruct", poll=True)

        with self.assertRaises(requests.exceptions.HTTPError):
            self.client.delete(instance.instance_id)

        instance = self.client.stop(instance.instance_id)
        instance_id = self.client.delete(instance.instance_id)
        self.assertEqual(instance.instance_id, instance_id)

    def test_delete_all_force(self) -> None:
        self.client.start("Qwen/Qwen2-7B-Instruct", poll=True)
        self.client.delete_all(force=True)
        instances = self.client.get_all_instances()
        self.assertEqual(len(instances), 0)


class TestModelAndHardwareTypes(unittest.TestCase):
    def setUp(self) -> None:
        load_dotenv()
        self.client = Cortecs()

    def test_get_all_models(self) -> None:
        models = self.client.get_all_models()
        self.assertIsInstance(models, list)

    def test_get_all_hardware_types(self) -> None:
        hardware_types = self.client.get_all_hardware_types()
        self.assertIsInstance(hardware_types, list)

    def test_get_available_hardware_types(self) -> None:
        hardware_types = self.client.get_available_hardware_types()
        self.assertIsInstance(hardware_types, list)

if __name__ == "__main__":
    unittest.main()
