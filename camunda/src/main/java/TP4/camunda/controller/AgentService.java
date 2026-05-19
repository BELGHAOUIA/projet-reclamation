package TP4.camunda.controller;

import org.camunda.bpm.engine.IdentityService;
import org.camunda.bpm.engine.identity.User;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Component("agentService")
public class AgentService {

    @Autowired
    private IdentityService identityService;

    public List<Map<String, String>> getAgentOptions() {
        List<User> allUsers = identityService.createUserQuery().list();

        return allUsers.stream()
                .filter(u -> u.getId() != null && u.getId().endsWith("agent"))
                .map(u -> {
                    Map<String, String> option = new HashMap<>();
                    String firstName = u.getFirstName() != null ? u.getFirstName() : "";
                    String lastName = u.getLastName() != null ? u.getLastName() : u.getId();

                    option.put("label", (firstName + " " + lastName).trim());
                    option.put("value", u.getId());
                    return option;
                })
                .collect(Collectors.toList());
    }
}
