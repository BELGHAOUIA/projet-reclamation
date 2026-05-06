package com.iset.Agent.repository;

import com.iset.Agent.entity.Agent;
import com.iset.Agent.enums.AgentLevel;
import com.iset.Agent.enums.AgentSpecialty;
import com.iset.Agent.enums.AgentStatus;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.List;

@Repository
public interface AgentRepository extends JpaRepository<Agent, String> {
    List<Agent> findByStatus(AgentStatus status);
    List<Agent> findByStatusAndSpecialty(AgentStatus status, AgentSpecialty specialty);
    List<Agent> findByStatusAndSpecialtyAndLevel(AgentStatus status, AgentSpecialty specialty, AgentLevel level);
    List<Agent> findByDepartment(String department);
    List<Agent> findByStatusAndDepartment(AgentStatus status, String department);
}