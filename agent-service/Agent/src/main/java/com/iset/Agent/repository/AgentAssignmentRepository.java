package com.iset.Agent.repository;

import com.iset.Agent.entity.AgentAssignment;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.List;
import java.util.Optional;

@Repository
public interface AgentAssignmentRepository extends JpaRepository<AgentAssignment, String> {
    List<AgentAssignment> findByAgentIdAndActiveTrue(String agentId);
    Optional<AgentAssignment> findByTicketIdAndActiveTrue(String ticketId);
    List<AgentAssignment> findByAgentId(String agentId);
}