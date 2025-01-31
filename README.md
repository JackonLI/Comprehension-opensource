# Xumi Comprehension Module

This repository provides key components essential for Xumi's Comprehension Module.

## Repository Structure

### `network/`  
Contains three synthetic network topologies of varying scales, along with their specifications:  
<table>
  <thead>
    <tr>
      <th rowspan="2"></th>
      <th colspan="4">Network Information</th>
      <th rowspan="2">#Prompt Tokens<br>(SNMT ratio)</th>
    </tr>
    <tr>
      <th>#Routers</th>
      <th>#Links</th>
      <th>#Interfaces</th>
      <th>#Entities</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>CampusNet</td>
      <td>41</td>
      <td>66</td>
      <td>361</td>
      <td>60</td>
      <td>4407 (51%)</td>
    </tr>
    <tr>
      <td>CloudNet</td>
      <td>171</td>
      <td>219</td>
      <td>2524</td>
      <td>352</td>
      <td>38755 (94%)</td>
    </tr>
    <tr>
      <td>ExtremeNet</td>
      <td>1026</td>
      <td>1236</td>
      <td>11796</td>
      <td>2062</td>
      <td>178414 (99%)</td>
    </tr>
  </tbody>
</table>

### `prompts/`  
Includes all the system prompts used in the experiments.

### `snmt/`  
Provides the SNMT for each network topology.

### `intent datasets/`  
Contains all evaluated natural language intents and their corresponding expected IR.
