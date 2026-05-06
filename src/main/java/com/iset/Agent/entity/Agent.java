package com.iset.Agent.entity;

import com.iset.Agent.enums.AgentLevel;
import com.iset.Agent.enums.AgentSpecialty;
import com.iset.Agent.enums.AgentStatus;
import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDateTime;
import java.util.List;

@Entity
@Table(name = "agents")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Agent {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private String id;

    @Column(nullable = false)
    private String firstName;

    @Column(nullable = false)
    private String lastName;

    @Column(nullable = false, unique = true)
    private String email;

    private String phone;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private AgentSpecialty specialty;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private AgentLevel level;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private AgentStatus status;

    @Column(nullable = false)
    private String department;

    @Column(nullable = false)
    private int maxTickets = 5;

    @Column(nullable = false)
    private int currentTicketCount = 0;

    @Column(updatable = false)
    private LocalDateTime createdAt;

    private LocalDateTime updatedAt;

    @OneToMany(mappedBy = "agent", cascade = CascadeType.ALL, fetch = FetchType.LAZY)
    private List<AgentAssignment> assignments;

    @PrePersist
    public void prePersist() {
        this.createdAt = LocalDateTime.now();
        this.updatedAt = LocalDateTime.now();
        if (this.status == null) this.status = AgentStatus.AVAILABLE;
    }

    @PreUpdate
    public void preUpdate() {
        this.updatedAt = LocalDateTime.now();
    }
}