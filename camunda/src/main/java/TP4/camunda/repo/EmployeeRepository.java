package TP4.camunda.repo;

import TP4.camunda.entity.Employee;
import org.springframework.data.repository.CrudRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface EmployeeRepository extends CrudRepository<Employee, Long> {
    boolean existsEmployeeByEmail(String email);
}